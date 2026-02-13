"""Transcript upload and retrieval endpoints."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models import Transcript, Company
from schemas.transcript import TranscriptResponse, TranscriptWithContent

router = APIRouter(prefix="/transcripts", tags=["transcripts"])


@router.post("/", response_model=TranscriptResponse, status_code=201)
async def upload_transcript(
    file: UploadFile = File(...),
    company_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a transcript file.
    
    For now, just stores the transcript. LLM extraction comes later.
    """
    # Validate company exists
    company = await db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with id {company_id} not found")
    
    # Validate file type
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")
    
    # Read content
    content = await file.read()
    try:
        content_str = content.decode("utf-8")
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
    
    return transcript


@router.get("/", response_model=list[TranscriptResponse])
async def list_transcripts(
    company_id: int | None = None,
    db: AsyncSession = Depends(get_db),
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
):
    """Get a single transcript with full content."""
    transcript = await db.get(Transcript, transcript_id)
    
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    return transcript