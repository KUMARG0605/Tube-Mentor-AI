"""Summary router - AI-powered video summarization with Groq LLM."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import SummaryRequest, SummaryResponse
from app.models.db_models import Summary, Transcript, Video
from app.services.summary import generate_summary

router = APIRouter(prefix="/api/summary", tags=["Summary"])


@router.post("/", response_model=SummaryResponse)
def create_summary(req: SummaryRequest, db: Session = Depends(get_db)):
    """Generate AI summary for a video. Requires transcript to exist first."""
    
    # Check if summary already exists (idempotency)
    existing = db.query(Summary).filter(Summary.video_id == req.video_id).first()
    if existing:
        video = db.query(Video).filter(Video.video_id == req.video_id).first()
        return SummaryResponse(
            video_id=existing.video_id,
            title=video.title if video else "Unknown",
            summary_text=existing.summary_text,
            key_topics=existing.key_topics or [],
        )

    # Verify transcript exists
    transcript = db.query(Transcript).filter(Transcript.video_id == req.video_id).first()
    if not transcript:
        raise HTTPException(
            status_code=400,
            detail="Transcript not found. Please fetch the transcript first.",
        )

    video = db.query(Video).filter(Video.video_id == req.video_id).first()
    title = video.title if video else "Untitled Video"

    # Generate summary via AI service
    try:
        result = generate_summary(title, transcript.content)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Summary generation failed: {str(e)}"
        )

    # Save to database
    summary = Summary(
        video_id=req.video_id,
        summary_text=result["summary_text"],
        key_topics=result["key_topics"],
    )
    db.add(summary)
    db.commit()

    return SummaryResponse(
        video_id=req.video_id,
        title=title,
        summary_text=result["summary_text"],
        key_topics=result["key_topics"],
    )


@router.get("/{video_id}", response_model=SummaryResponse)
def get_summary(video_id: str, db: Session = Depends(get_db)):
    """Get a previously generated summary from the database."""
    existing = db.query(Summary).filter(Summary.video_id == video_id).first()
    if not existing:
        raise HTTPException(
            status_code=404, 
            detail="Summary not found. Generate it first via POST."
        )

    video = db.query(Video).filter(Video.video_id == video_id).first()
    return SummaryResponse(
        video_id=existing.video_id,
        title=video.title if video else "Unknown",
        summary_text=existing.summary_text,
        key_topics=existing.key_topics or [],
    )
