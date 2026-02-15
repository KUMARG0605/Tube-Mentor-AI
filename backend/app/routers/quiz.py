"""Quiz router - AI-generated quiz questions from video content."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import QuizRequest, QuizResponse
from app.models.db_models import Quiz, Transcript, Video
from app.services.quiz import generate_quiz

router = APIRouter(prefix="/api/quiz", tags=["Quiz"])


@router.post("/", response_model=QuizResponse)
def create_quiz(req: QuizRequest, db: Session = Depends(get_db)):
    """Generate a quiz for a video using its transcript."""
    
    # Check if quiz already exists
    existing = db.query(Quiz).filter(Quiz.video_id == req.video_id).first()
    if existing:
        video = db.query(Video).filter(Video.video_id == req.video_id).first()
        return QuizResponse(
            video_id=existing.video_id,
            title=video.title if video else "Unknown",
            total_questions=existing.total_questions,
            questions=existing.questions,
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

    # Generate quiz with AI
    try:
        questions = generate_quiz(title, transcript.content, req.num_questions)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Quiz generation failed: {str(e)}"
        )

    # Save to database
    quiz = Quiz(
        video_id=req.video_id,
        questions=questions,
        total_questions=len(questions),
    )
    db.add(quiz)
    db.commit()

    return QuizResponse(
        video_id=req.video_id,
        title=title,
        total_questions=len(questions),
        questions=questions,
    )


@router.get("/{video_id}", response_model=QuizResponse)
def get_quiz(video_id: str, db: Session = Depends(get_db)):
    """Get a previously generated quiz."""
    existing = db.query(Quiz).filter(Quiz.video_id == video_id).first()
    if not existing:
        raise HTTPException(
            status_code=404, 
            detail="Quiz not found. Generate it first via POST."
        )

    video = db.query(Video).filter(Video.video_id == video_id).first()
    return QuizResponse(
        video_id=existing.video_id,
        title=video.title if video else "Unknown",
        total_questions=existing.total_questions,
        questions=existing.questions,
    )
