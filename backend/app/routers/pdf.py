"""PDF Router - Generate downloadable study notes as PDF files."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import PDFRequest, PDFResponse
from app.models.db_models import Summary, Quiz, Video
from app.services.pdf_generator import generate_pdf
from app.config import settings

router = APIRouter(prefix="/api/pdf", tags=["PDF"])


@router.post("/", response_model=PDFResponse)
def create_pdf(req: PDFRequest, db: Session = Depends(get_db)):
    """Generate a PDF with summary notes and quiz for a video."""
    video = db.query(Video).filter(Video.video_id == req.video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found in database.")

    title = video.title

    summary_text = ""
    key_topics = []
    if req.include_summary:
        summary = db.query(Summary).filter(Summary.video_id == req.video_id).first()
        if not summary:
            raise HTTPException(
                status_code=400,
                detail="Summary not found. Generate a summary first.",
            )
        summary_text = summary.summary_text
        key_topics = summary.key_topics or []

    questions = []
    if req.include_quiz:
        quiz = db.query(Quiz).filter(Quiz.video_id == req.video_id).first()
        if not quiz:
            raise HTTPException(
                status_code=400,
                detail="Quiz not found. Generate a quiz first.",
            )
        questions = quiz.questions

    try:
        file_name = generate_pdf(
            video_id=req.video_id,
            title=title,
            summary_text=summary_text,
            key_topics=key_topics,
            questions=questions,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"PDF generation failed: {str(e)}"
        )

    return PDFResponse(
        video_id=req.video_id,
        title=title,
        file_name=file_name,
        download_url=f"/api/pdf/download/{file_name}",
    )


@router.get("/download/{file_name}")
def download_pdf(file_name: str):
    """Download a previously generated PDF file."""
    file_path = settings.PDF_DIR / file_name
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found.")

    return FileResponse(
        path=str(file_path),
        filename=file_name,
        media_type="application/pdf",
    )
