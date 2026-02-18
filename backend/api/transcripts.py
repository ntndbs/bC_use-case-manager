"""Transcript upload and retrieval endpoints."""

import logging
from pathlib import Path
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user, require_role
from db.database import get_db
from db.models import Transcript, Company, UseCase, User, Role
from schemas.transcript import TranscriptResponse, TranscriptWithContent, TranscriptWithUseCases
from schemas.use_case import UseCaseResponse
from services.extraction import extract_use_cases, ExtractionError

logger = logging.getLogger(__name__)

TRANSCRIPTS_DIR = Path(__file__).resolve().parents[1] / "data" / "transcripts"
TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

def _safe_filename(name: str) -> str:
    return Path(name).name

router = APIRouter(prefix="/transcripts", tags=["transcripts"])


async def _extract_and_persist(
    transcript: Transcript, db: AsyncSession
) -> list[UseCase]:
    """Run LLM extraction on a transcript and save the use cases to DB."""
    extracted = await extract_use_cases(transcript.content)

    use_cases = []
    for item in extracted:
        uc = UseCase(
            title=item.title,
            description=item.description,
            stakeholders=[s.model_dump() for s in item.stakeholders],
            expected_benefit=item.expected_benefit,
            company_id=transcript.company_id,
            transcript_id=transcript.id,
        )
        db.add(uc)
        use_cases.append(uc)

    await db.commit()
    for uc in use_cases:
        await db.refresh(uc)

    return use_cases


@router.post("/", response_model=TranscriptWithUseCases, status_code=201)
async def upload_transcript(
    file: UploadFile = File(...),
    company_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(Role.MAINTAINER)),
):
    """Upload a transcript file and automatically extract use cases via LLM."""
    # Validate company exists
    company = await db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with id {company_id} not found")

    # Validate file type
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")

    # Read content
    content = await file.read()
    if not content or not content.strip():
        raise HTTPException(status_code=400, detail="File is empty")
    try:
        content_str = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")

    # Create transcript
    transcript = Transcript(
        filename=file.filename,
        content=content_str,
        company_id=company_id,
        # uploaded_by_id=current_user.id  # TODO: Add after auth
    )

    db.add(transcript)
    await db.commit()
    await db.refresh(transcript)

    stored_name = f"{transcript.id}_{uuid.uuid4().hex}_{_safe_filename(file.filename)}"
    stored_path = TRANSCRIPTS_DIR / stored_name
    try:
        stored_path.write_bytes(content)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to persist transcript file")

    # Extract use cases automatically
    try:
        use_cases = await _extract_and_persist(transcript, db)
    except ExtractionError as e:
        logger.error("Extraction failed for transcript %d: %s", transcript.id, e)
        use_cases = []

    return TranscriptWithUseCases(
        id=transcript.id,
        filename=transcript.filename,
        company_id=transcript.company_id,
        created_at=transcript.created_at,
        uploaded_by_id=transcript.uploaded_by_id,
        use_cases=use_cases,
    )


@router.get("/", response_model=list[TranscriptResponse])
async def list_transcripts(
    company_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """List all transcripts, optionally filtered by company."""
    query = select(Transcript)
    
    if company_id:
        query = query.where(Transcript.company_id == company_id)
    
    query = query.order_by(Transcript.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{transcript_id}", response_model=TranscriptWithContent)
async def get_transcript(
    transcript_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Get a single transcript with full content."""
    transcript = await db.get(Transcript, transcript_id)
    
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    return transcript


@router.post("/{transcript_id}/extract", response_model=list[UseCaseResponse], status_code=201)
async def extract_use_cases_from_transcript(
    transcript_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(Role.MAINTAINER)),
):
    """Extract use cases from a transcript via LLM.

    Sends the transcript content to the LLM, validates the structured
    response, and persists the extracted use cases in the database.
    Retries up to 2 times on validation failure.
    """
    transcript = await db.get(Transcript, transcript_id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    try:
        use_cases = await _extract_and_persist(transcript, db)
    except ExtractionError as e:
        logger.error("Extraction failed for transcript %d: %s", transcript_id, e)
        raise HTTPException(status_code=502, detail=str(e))

    logger.info(
        "Extracted %d use cases from transcript %d", len(use_cases), transcript_id
    )
    return use_cases