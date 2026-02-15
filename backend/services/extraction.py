"""Use Case extraction from workshop transcripts via LLM."""

import logging

from pydantic import ValidationError

from schemas.extraction import ExtractionResult, ExtractedUseCase
from services.llm import chat_completion_json

logger = logging.getLogger(__name__)

MAX_RETRIES = 2

SYSTEM_PROMPT = """\
Du bist ein Experte für die Analyse von Workshop-Transkripten.

Deine Aufgabe: Extrahiere alle Use Cases aus dem folgenden Transkript.

Für jeden Use Case liefere:
- **title**: Kurzer, prägnanter Titel (max. 100 Zeichen)
- **description**: Ausführliche Beschreibung des Problems und der gewünschten Lösung
- **stakeholders**: Liste der beteiligten Personen mit Name und Rolle im Unternehmen
- **expected_benefit**: Konkreter erwarteter Nutzen / Mehrwert

Regeln:
- Extrahiere NUR Use Cases, die tatsächlich im Transkript besprochen werden.
- Ein Use Case beschreibt ein konkretes Problem und eine gewünschte Lösung.
- Stakeholders sind die Personen, die den Use Case im Workshop angesprochen haben.
- Antworte ausschließlich mit validem JSON, kein anderer Text.

Antwortformat:
{
  "use_cases": [
    {
      "title": "...",
      "description": "...",
      "stakeholders": [{"name": "...", "role": "..."}],
      "expected_benefit": "..."
    }
  ]
}\
"""


async def extract_use_cases(transcript_content: str) -> list[ExtractedUseCase]:
    """Extract use cases from a transcript using the LLM.

    Sends the transcript to the LLM, validates the response against
    the ExtractionResult schema, and retries up to MAX_RETRIES times
    if validation fails.

    Args:
        transcript_content: The full text of the workshop transcript.

    Returns:
        List of extracted use cases.

    Raises:
        ExtractionError: If extraction fails after all retries.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": transcript_content},
    ]

    last_error = None

    for attempt in range(1 + MAX_RETRIES):
        try:
            logger.info("Extraction attempt %d/%d", attempt + 1, 1 + MAX_RETRIES)

            data = await chat_completion_json(messages)
            result = ExtractionResult.model_validate(data)

            logger.info("Extraction successful: %d use cases", len(result.use_cases))
            return result.use_cases

        except (ValueError, ValidationError) as e:
            last_error = e
            logger.warning("Extraction attempt %d failed: %s", attempt + 1, e)

            if attempt < MAX_RETRIES:
                # Add error feedback for the LLM to correct itself
                messages.append({
                    "role": "assistant",
                    "content": str(data) if isinstance(e, ValidationError) else "",
                })
                messages.append({
                    "role": "user",
                    "content": (
                        f"Deine Antwort war kein valides Format. Fehler: {e}\n\n"
                        "Bitte antworte erneut mit validem JSON im geforderten Format."
                    ),
                })

    raise ExtractionError(
        f"Use Case extraction failed after {1 + MAX_RETRIES} attempts: {last_error}"
    )


class ExtractionError(Exception):
    """Raised when LLM extraction fails after all retries."""
