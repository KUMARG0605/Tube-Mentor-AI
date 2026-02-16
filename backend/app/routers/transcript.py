"""Transcript router - fetch and store YouTube video transcripts."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.schemas import TranscriptRequest, TranscriptResponse
from app.models.db_models import Transcript, Video, Summary
from app.services.transcript import get_transcript

# Phase 2: Auto-index for recommendations
try:
    from app.services.vector_store import get_vector_store
    from app.services.embeddings import generate_embedding, create_video_text
    PHASE2_ENABLED = True
except ImportError:
    PHASE2_ENABLED = False

router = APIRouter(prefix="/api/transcript", tags=["Transcript"])


def auto_index_video(video_id: str, transcript_content: str, db: Session):
    """Auto-index video for recommendations when transcript is created."""
    if not PHASE2_ENABLED:
        return
    
    try:
        store = get_vector_store()
        
        # Get video metadata
        video = db.query(Video).filter(Video.video_id == video_id).first()
        title = video.title if video else f"Video {video_id}"
        thumbnail_url = video.thumbnail_url if video else ""
        channel_name = video.channel_name if video else ""
        
        # Get summary if exists
        summary_obj = db.query(Summary).filter(Summary.video_id == video_id).first()
        summary_text = summary_obj.summary_text if summary_obj else ""
        
        # Create embedding with transcript content
        text = create_video_text(
            str(title),
            "",  # description
            str(summary_text or ""),
            str(transcript_content)  # KEY: transcript for content-based matching
        )
        embedding = generate_embedding(text)
        
        # Add to index
        store.add_video(
            video_id=video_id,
            title=str(title),
            embedding=embedding,
            description="",
            summary=str(summary_text or ""),
            thumbnail_url=str(thumbnail_url or ""),
            channel_name=str(channel_name or ""),
        )
    except Exception as e:
        # Don't fail transcript fetch if indexing fails
        print(f"Auto-index failed for {video_id}: {e}")


@router.post("/", response_model=TranscriptResponse)
def fetch_transcript(req: TranscriptRequest, db: Session = Depends(get_db)):
    """Fetch and store transcript for a YouTube video."""
    existing = db.query(Transcript).filter(Transcript.video_id == req.video_id).first()
    
    if existing:
        # Auto-index if not already indexed (Phase 2)
        auto_index_video(existing.video_id, existing.content, db)
        
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

    try:
        transcript = Transcript(
            video_id=result["video_id"],
            language=result["language"],
            content=result["content"],
        )
        db.add(transcript)
        db.commit()
        db.refresh(transcript)
        
        # Auto-index for recommendations (Phase 2)
        auto_index_video(result["video_id"], result["content"], db)
        
    except IntegrityError:
        # Race condition: another request inserted it first, rollback and fetch existing
        db.rollback()
        existing = db.query(Transcript).filter(Transcript.video_id == req.video_id).first()
        if existing:
            return TranscriptResponse(
                video_id=existing.video_id,
                language=existing.language,
                content=existing.content,
                word_count=len(existing.content.split()),
            )

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
