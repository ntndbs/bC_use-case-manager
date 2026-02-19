"""OpenRouter LLM client using the OpenAI-compatible API."""

import json
import logging

from openai import AsyncOpenAI

from core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

client = AsyncOpenAI(
    base_url=settings.openrouter_base_url,
    api_key=settings.openrouter_api_key,
)


async def chat_completion(
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.2,
) -> str:
    """Send messages to OpenRouter and return the assistant's text response.

    Args:
        messages: OpenAI-format messages (role + content).
        model: Override the default model from settings.
        temperature: Sampling temperature (low = more deterministic).

    Returns:
        The assistant message content as a string.

    Raises:
        RuntimeError: If the API call fails or returns no content.
    """
    model = model or settings.openrouter_model

    logger.info("LLM request: model=%s, messages=%d", model, len(messages))

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("LLM returned empty response")

    logger.info("LLM response: %d chars", len(content))
    return content


async def chat_completion_json(
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.2,
) -> dict:
    """Send messages and parse the response as JSON.

    Raises:
        ValueError: If the response is not valid JSON.
    """
    raw = await chat_completion(messages, model, temperature)

    # Strip markdown code fences if present
    text = raw.strip()
    if text.startswith("```"):
        # Remove opening fence (```json or ```)
        first_newline = text.index("\n")
        text = text[first_newline + 1:]
        # Remove closing fence
        if text.endswith("```"):
            text = text[:-3].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM response is not valid JSON: {e}\nRaw: {raw[:500]}")
