"""Pydantic schemas for LLM extraction output validation."""

from pydantic import BaseModel, Field

from schemas.use_case import Stakeholder


class ExtractedUseCase(BaseModel):
    """A single use case extracted by the LLM."""

    title: str = Field(..., min_length=1, description="Kurzer, prägnanter Titel des Use Cases")
    description: str = Field(..., min_length=1, description="Ausführliche Beschreibung des Use Cases")
    stakeholders: list[Stakeholder] = Field(
        default_factory=list, description="Beteiligte Personen mit Name und Rolle"
    )
    expected_benefit: str = Field(..., min_length=1, description="Erwarteter Nutzen / Mehrwert")


class ExtractionResult(BaseModel):
    """Complete extraction result from the LLM."""

    use_cases: list[ExtractedUseCase] = Field(
        ..., min_length=1, description="Liste der extrahierten Use Cases"
    )
