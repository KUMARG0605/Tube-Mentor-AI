"""Transcript router - fetch and store YouTube video transcripts."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import TranscriptRequest, TranscriptResponse
from app.models.db_models import Transcript, Video
from app.services.transcript import get_transcript

router = APIRouter(prefix="/api/transcript", tags=["Transcript"])


@router.post("/", response_model=TranscriptResponse)
def fetch_transcript(req: TranscriptRequest, db: Session = Depends(get_db)):
    """Fetch and store transcript for a YouTube video."""
    existing = db.query(Transcript).filter(Transcript.video_id == req.video_id).first()
    
    if existing:
        return TranscriptResponse(
            video_id=existing.video_id,
            language=existing.language,
            content=existing.content,
            word_count=len(existing.content.split()),
        )

    try:
        result = get_transcript(req.video_id, req.language)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    transcript = Transcript(
        video_id=result["video_id"],
        language=result["language"],
        content=result["content"],
    )
    db.add(transcript)
    db.commit()

    return TranscriptResponse(**result)


@router.get("/{video_id}", response_model=TranscriptResponse)
def get_stored_transcript(video_id: str, db: Session = Depends(get_db)):
    """Get a previously fetched transcript from the database."""
    existing = db.query(Transcript).filter(Transcript.video_id == video_id).first()
    
    if not existing:
        raise HTTPException(
            status_code=404, 
            detail="Transcript not found. Fetch it first via POST."
        )

    return TranscriptResponse(
        video_id=existing.video_id,
        language=existing.language,
        content=existing.content,
        word_count=len(existing.content.split()),
    )
