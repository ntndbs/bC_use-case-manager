"""Agent service: tool-calling loop with conversation memory."""

import json
import logging

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from db.models import User
from services.tools import TOOL_DEFINITIONS, execute_tool
import services.tool_handlers  # noqa: F401 — registers all tools on import

logger = logging.getLogger(__name__)

settings = get_settings()

_client = AsyncOpenAI(
    base_url=settings.openrouter_base_url,
    api_key=settings.openrouter_api_key,
)

SYSTEM_PROMPT = """\
Du bist ein hilfreicher Assistent für das BadenCampus Use-Case-Management-System.
Du hilfst Nutzern dabei, Use Cases aus Workshop-Transkripten zu verwalten.

Deine Fähigkeiten:
- Use Cases auflisten, anzeigen, erstellen, bearbeiten, Status ändern, archivieren
- Transkripte analysieren und Use Cases daraus extrahieren
- Angehängte Transkript-Dateien speichern und auswerten
- Unternehmen auflisten

Regeln:
- Antworte auf Deutsch, es sei denn der Nutzer schreibt auf Englisch.
- Wenn eine Anfrage mehrdeutig ist (z.B. "den Use Case" ohne ID oder klaren Bezug), \
frag den Nutzer nach Klarstellung statt zu raten.
- KRITISCH: Du MUSST bei JEDER Frage zu Daten (Use Cases, Unternehmen, Branchen, \
Transkripte) das passende Tool aufrufen. Das gilt auch für Folgefragen im selben \
Gespräch. Nutze NIEMALS vorherige Antworten oder den Gesprächsverlauf als Datenquelle. \
Rufe IMMER das Tool erneut auf, selbst wenn du glaubst die Antwort bereits zu kennen.
- Wenn du Tool-Ergebnisse erhältst, liste die konkreten Daten auf. \
Beispiel: Wenn list_use_cases 3 Use Cases zurückgibt, antworte so:
  1. UC #1: "Titel A" (Status: new)
  2. UC #2: "Titel B" (Status: approved)
  3. UC #3: "Titel C" (Status: completed)
Fasse NIEMALS eine Liste als "Es gibt X Einträge" zusammen, ohne die Einträge \
einzeln aufzulisten. Das gilt für Use Cases, Unternehmen, Branchen und alle anderen Daten.
- Halte Antworten kurz und prägnant.
"""

MAX_TOOL_ROUNDS = 10

# In-memory conversation storage (keyed by session_id)
_sessions: dict[str, list[dict]] = {}

# Temporary file storage for chat uploads (keyed by session_id)
_file_store: dict[str, dict] = {}


def store_file(session_id: str, filename: str, content: str) -> None:
    """Store an uploaded file for later use by tools."""
    _file_store[session_id] = {"filename": filename, "content": content}


def get_file(session_id: str) -> dict | None:
    """Retrieve and remove the stored file for a session."""
    return _file_store.pop(session_id, None)


def _get_history(session_id: str) -> list[dict]:
    """Get or create conversation history for a session."""
    if session_id not in _sessions:
        _sessions[session_id] = []
    return _sessions[session_id]


async def run_agent(
    user_message: str,
    session_id: str,
    db: AsyncSession,
    user: User | None = None,
) -> tuple[str, list[str]]:
    """Run the agent loop for a user message.

    Returns:
        Tuple of (assistant_reply, list_of_tool_names_called).
    """
    history = _get_history(session_id)
    history.append({"role": "user", "content": user_message})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    tools_called: list[str] = []

    for _ in range(MAX_TOOL_ROUNDS):
        kwargs = {
            "model": settings.openrouter_model,
            "messages": messages,
            "temperature": 0.3,
        }
        if TOOL_DEFINITIONS:
            kwargs["tools"] = TOOL_DEFINITIONS
            kwargs["tool_choice"] = "auto"

        response = await _client.chat.completions.create(**kwargs)
        choice = response.choices[0]

        # If the model wants to call tools
        if choice.message.tool_calls:
            # Append assistant message with tool calls
            messages.append(choice.message.model_dump())

            for tool_call in choice.message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments or "{}")

                logger.info("Tool call: %s(%s)", fn_name, fn_args)
                tools_called.append(fn_name)

                result = await execute_tool(fn_name, fn_args, db, user, session_id)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

            continue  # Next round — let the LLM process tool results

        # No tool calls — we have the final text response
        reply = choice.message.content or ""
        history.append({"role": "assistant", "content": reply})

        logger.info(
            "Agent reply (session=%s, tools=%d): %s",
            session_id, len(tools_called), reply[:100],
        )
        return reply, tools_called

    # Safety: max rounds exceeded
    fallback = "Entschuldigung, ich konnte die Anfrage nicht abschließen. Bitte versuche es erneut."
    history.append({"role": "assistant", "content": fallback})
    return fallback, tools_called
