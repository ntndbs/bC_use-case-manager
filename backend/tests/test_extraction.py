"""Tests for extract_use_cases() with mocked LLM responses (#176).

Mocks chat_completion_json to test JSON parsing, Pydantic validation,
and retry logic without making real API calls.
"""

import pytest
from unittest.mock import AsyncMock, patch

from services.extraction import extract_use_cases, ExtractionError


VALID_LLM_RESPONSE = {
    "use_cases": [
        {
            "title": "KI-gestützte Kundenanalyse",
            "description": "Automatische Analyse von Kundendaten zur Erkennung von Abwanderungsrisiken.",
            "stakeholders": [
                {"name": "Max Müller", "role": "Vertriebsleiter"},
                {"name": "Anna Schmidt", "role": "Data Analyst"},
            ],
            "expected_benefit": "20% weniger Kundenabwanderung durch frühzeitige Intervention.",
        },
        {
            "title": "Chatbot für Mitarbeiter-FAQ",
            "description": "Ein interner Chatbot, der häufige HR-Fragen automatisch beantwortet.",
            "stakeholders": [{"name": "Lisa Weber", "role": "HR-Leiterin"}],
            "expected_benefit": "Entlastung des HR-Teams um ca. 10 Stunden pro Woche.",
        },
    ]
}


@pytest.mark.asyncio
@patch("services.extraction.chat_completion_json", new_callable=AsyncMock)
async def test_extract_valid_response(mock_llm: AsyncMock):
    """Valid LLM JSON is parsed into ExtractedUseCase objects."""
    mock_llm.return_value = VALID_LLM_RESPONSE

    result = await extract_use_cases("Fake transcript content")

    assert len(result) == 2
    assert result[0].title == "KI-gestützte Kundenanalyse"
    assert len(result[0].stakeholders) == 2
    assert result[1].title == "Chatbot für Mitarbeiter-FAQ"
    mock_llm.assert_called_once()


@pytest.mark.asyncio
@patch("services.extraction.chat_completion_json", new_callable=AsyncMock)
async def test_extract_single_use_case(mock_llm: AsyncMock):
    """Single use case in response is handled correctly."""
    mock_llm.return_value = {
        "use_cases": [
            {
                "title": "Prozessautomatisierung",
                "description": "Automatisierung manueller Rechnungsprüfung.",
                "stakeholders": [],
                "expected_benefit": "Zeitersparnis von 5h/Woche.",
            }
        ]
    }

    result = await extract_use_cases("Some transcript")

    assert len(result) == 1
    assert result[0].title == "Prozessautomatisierung"
    assert result[0].stakeholders == []


@pytest.mark.asyncio
@patch("services.extraction.chat_completion_json", new_callable=AsyncMock)
async def test_extract_empty_use_cases_fails(mock_llm: AsyncMock):
    """Empty use_cases list fails Pydantic validation (min_length=1) and retries."""
    mock_llm.return_value = {"use_cases": []}

    with pytest.raises(ExtractionError):
        await extract_use_cases("Some transcript")

    # 1 initial + 2 retries = 3 calls
    assert mock_llm.call_count == 3


@pytest.mark.asyncio
@patch("services.extraction.chat_completion_json", new_callable=AsyncMock)
async def test_extract_missing_field_fails(mock_llm: AsyncMock):
    """Missing required field triggers validation error and retries."""
    mock_llm.return_value = {
        "use_cases": [
            {
                "title": "Incomplete",
                # missing: description, expected_benefit
            }
        ]
    }

    with pytest.raises(ExtractionError):
        await extract_use_cases("Some transcript")

    assert mock_llm.call_count == 3


@pytest.mark.asyncio
@patch("services.extraction.chat_completion_json", new_callable=AsyncMock)
async def test_extract_invalid_json_from_llm(mock_llm: AsyncMock):
    """ValueError from chat_completion_json (invalid JSON) triggers retries."""
    mock_llm.side_effect = ValueError("not valid JSON")

    with pytest.raises(ExtractionError):
        await extract_use_cases("Some transcript")

    assert mock_llm.call_count == 3


@pytest.mark.asyncio
@patch("services.extraction.chat_completion_json", new_callable=AsyncMock)
async def test_extract_retry_then_succeed(mock_llm: AsyncMock):
    """First attempt fails, second succeeds — retries work."""
    mock_llm.side_effect = [
        {"use_cases": []},  # fails validation (min_length=1)
        VALID_LLM_RESPONSE,  # succeeds
    ]

    result = await extract_use_cases("Some transcript")

    assert len(result) == 2
    assert mock_llm.call_count == 2
