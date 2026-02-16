"""Content Generation Router - Phase 3 API endpoints for content creation."""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from pathlib import Path

from app.database import get_db
from app.models.db_models import Video, Summary, Transcript


router = APIRouter(prefix="/api/content", tags=["Content Generation"])


# ============== Request/Response Models ==============

class ScriptRequest(BaseModel):
    """Request to generate a video script."""
    video_id: Optional[str] = None
    topic: Optional[str] = None
    style: str = Field(default="educational", description="Script style")
    audience: str = Field(default="general", description="Target audience")
    duration: int = Field(default=10, ge=1, le=60, description="Target duration in minutes")


class ScriptResponse(BaseModel):
    """Generated script response."""
    script: str
    word_count: int
    estimated_duration_minutes: int
    title: Optional[str] = None
    topic: Optional[str] = None


class SlidesRequest(BaseModel):
    """Request to generate presentation slides."""
    video_id: str
    include_images: bool = False


class SlidesResponse(BaseModel):
    """Generated slides response."""
    filename: str
    filepath: str
    slide_count: int
    title: str
    download_url: str


class ImageSearchRequest(BaseModel):
    """Request for image search."""
    query: str
    count: int = Field(default=5, ge=1, le=20)
    orientation: str = Field(default="landscape")


class ImageResult(BaseModel):
    """Single image result."""
    id: str
    description: str
    urls: dict
    author: dict
    attribution: str


class VoiceRequest(BaseModel):
    """Request for text-to-speech."""
    text: str = Field(..., min_length=1, max_length=5000)
    voice_id: Optional[str] = None


class VoiceResponse(BaseModel):
    """Generated voice response."""
    success: bool
    filename: Optional[str] = None
    filepath: Optional[str] = None
    duration_seconds: Optional[float] = None
    error: Optional[str] = None
    download_url: Optional[str] = None


class VideoGenerateRequest(BaseModel):
    """Request to generate video."""
    video_id: str
    include_audio: bool = False
    voice_id: Optional[str] = None


class VideoStatusResponse(BaseModel):
    """Video generation status."""
    available: bool
    dependencies: dict
    message: str


# ============== Script Endpoints ==============

@router.post("/script/from-video", response_model=ScriptResponse)
async def generate_script_from_video(
    request: ScriptRequest,
    db: Session = Depends(get_db)
):
    """Generate a video script from an existing video's content."""
    if not request.video_id:
        raise HTTPException(400, "video_id is required")
    
    # Get video data
    video = db.query(Video).filter(Video.video_id == request.video_id).first()
    summary_obj = db.query(Summary).filter(Summary.video_id == request.video_id).first()
    transcript_obj = db.query(Transcript).filter(Transcript.video_id == request.video_id).first()
    
    if not summary_obj and not transcript_obj:
        raise HTTPException(404, "No content found for this video. Generate summary first.")
    
    title = video.title if video else f"Video {request.video_id}"
    summary = summary_obj.summary_text if summary_obj else ""
    transcript = transcript_obj.content if transcript_obj else ""
    
    from app.services.script_generator import generate_video_script
    
    result = generate_video_script(
        title=title,
        summary=summary,
        transcript=transcript,
        duration=request.duration
    )
    
    return ScriptResponse(
        script=result["script"],
        word_count=result["word_count"],
        estimated_duration_minutes=result["estimated_duration_minutes"],
        title=title,
    )


@router.post("/script/custom", response_model=ScriptResponse)
async def generate_custom_script(request: ScriptRequest):
    """Generate a custom script on any topic."""
    if not request.topic:
        raise HTTPException(400, "topic is required for custom script")
    
    from app.services.script_generator import generate_custom_script
    
    result = generate_custom_script(
        topic=request.topic,
        style=request.style,
        audience=request.audience,
        duration=request.duration
    )
    
    return ScriptResponse(
        script=result["script"],
        word_count=result["word_count"],
        estimated_duration_minutes=result["estimated_duration_minutes"],
        topic=request.topic,
    )


# ============== Slides Endpoints ==============

@router.post("/slides", response_model=SlidesResponse)
async def generate_slides(
    request: SlidesRequest,
    db: Session = Depends(get_db)
):
    """Generate PowerPoint presentation from video summary."""
    video = db.query(Video).filter(Video.video_id == request.video_id).first()
    summary_obj = db.query(Summary).filter(Summary.video_id == request.video_id).first()
    
    if not summary_obj:
        raise HTTPException(404, "Summary not found. Generate summary first.")
    
    title = video.title if video else f"Video {request.video_id}"
    key_topics = summary_obj.key_topics if summary_obj else []
    
    from app.services.slides_generator import generate_presentation
    
    result = generate_presentation(
        title=title,
        summary=summary_obj.summary_text,
        key_topics=key_topics,
        video_id=request.video_id
    )
    
    return SlidesResponse(
        filename=result["filename"],
        filepath=result["filepath"],
        slide_count=result["slide_count"],
        title=title,
        download_url=f"/api/content/slides/download/{result['filename']}"
    )


@router.get("/slides/download/{filename}")
async def download_slides(filename: str):
    """Download generated presentation file."""
    from app.services.slides_generator import SLIDES_DIR
    
    filepath = SLIDES_DIR / filename
    if not filepath.exists():
        raise HTTPException(404, "File not found")
    
    return FileResponse(
        str(filepath),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=filename
    )


# ============== Image Endpoints ==============

@router.post("/images/search", response_model=List[ImageResult])
async def search_images(request: ImageSearchRequest):
    """Search for relevant images using Unsplash."""
    from app.services.image_service import search_images
    
    images = await search_images(
        query=request.query,
        count=request.count,
        orientation=request.orientation
    )
    
    return images


@router.get("/images/for-video/{video_id}", response_model=List[ImageResult])
async def get_images_for_video(
    video_id: str,
    count: int = 5,
    db: Session = Depends(get_db)
):
    """Get relevant images for a video based on its content."""
    summary_obj = db.query(Summary).filter(Summary.video_id == video_id).first()
    
    if not summary_obj:
        raise HTTPException(404, "Summary not found. Generate summary first.")
    
    from app.services.image_service import search_images, extract_keywords_for_images
    
    # Extract keywords from summary
    keywords = extract_keywords_for_images(summary_obj.summary_text)
    query = " ".join(keywords[:3])  # Use top 3 keywords
    
    images = await search_images(query=query, count=count)
    
    return images


# ============== Voice Endpoints ==============

@router.get("/voice/voices")
async def get_voices():
    """Get available voice options."""
    from app.services.voice_service import get_available_voices
    
    voices = await get_available_voices()
    return {"voices": voices}


@router.post("/voice/generate", response_model=VoiceResponse)
async def generate_voice(request: VoiceRequest):
    """Convert text to speech."""
    from app.services.voice_service import generate_speech
    
    result = await generate_speech(
        text=request.text,
        voice_id=request.voice_id
    )
    
    if result["success"]:
        return VoiceResponse(
            success=True,
            filename=result["filename"],
            filepath=result["filepath"],
            duration_seconds=result["estimated_duration_seconds"],
            download_url=f"/api/content/voice/download/{result['filename']}"
        )
    else:
        return VoiceResponse(
            success=False,
            error=result["error"]
        )


@router.post("/voice/from-script/{video_id}", response_model=VoiceResponse)
async def generate_voice_from_script(
    video_id: str,
    voice_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Generate voice narration for a video's summary."""
    summary_obj = db.query(Summary).filter(Summary.video_id == video_id).first()
    
    if not summary_obj:
        raise HTTPException(404, "Summary not found. Generate summary first.")
    
    from app.services.voice_service import generate_speech
    
    # Use summary as script (limited to avoid high costs)
    text = summary_obj.summary_text[:4000]
    
    result = await generate_speech(text=text, voice_id=voice_id)
    
    if result["success"]:
        return VoiceResponse(
            success=True,
            filename=result["filename"],
            filepath=result["filepath"],
            duration_seconds=result["estimated_duration_seconds"],
            download_url=f"/api/content/voice/download/{result['filename']}"
        )
    else:
        return VoiceResponse(
            success=False,
            error=result["error"]
        )


@router.get("/voice/download/{filename}")
async def download_voice(filename: str):
    """Download generated audio file."""
    from app.services.voice_service import AUDIO_DIR
    
    filepath = AUDIO_DIR / filename
    if not filepath.exists():
        raise HTTPException(404, "File not found")
    
    return FileResponse(
        str(filepath),
        media_type="audio/mpeg",
        filename=filename
    )


@router.get("/voice/cost-estimate")
async def estimate_voice_cost(text_length: int):
    """Estimate cost for text-to-speech conversion."""
    from app.services.voice_service import get_character_count
    
    # Create dummy text of specified length
    result = get_character_count("x" * text_length)
    return result


# ============== Video Endpoints ==============

@router.get("/video/status", response_model=VideoStatusResponse)
async def get_video_status():
    """Check if video generation is available."""
    from app.services.video_generator import get_video_status
    
    status = get_video_status()
    return VideoStatusResponse(**status)


@router.post("/video/generate/{video_id}")
async def generate_video(
    video_id: str,
    include_audio: bool = False,
    voice_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Generate a video from slides and optional audio narration.
    
    This is a complex operation that:
    1. Creates slides from summary
    2. Optionally generates audio narration
    3. Combines into a video
    """
    from app.services.video_generator import get_video_status, generate_slideshow_video
    
    # Check if video generation is available
    status = get_video_status()
    if not status["available"]:
        raise HTTPException(503, f"Video generation unavailable: {status['message']}")
    
    # Get content
    video = db.query(Video).filter(Video.video_id == video_id).first()
    summary_obj = db.query(Summary).filter(Summary.video_id == video_id).first()
    
    if not summary_obj:
        raise HTTPException(404, "Summary not found. Generate summary first.")
    
    title = video.title if video else f"Video {video_id}"
    key_topics = summary_obj.key_topics or []
    
    # Create slides data
    slides = [
        {"type": "text", "content": title, "duration": 5.0},
    ]
    
    # Add topic slides
    for topic in key_topics[:5]:
        slides.append({
            "type": "text",
            "content": topic,
            "duration": 8.0
        })
    
    # Add conclusion
    slides.append({
        "type": "text",
        "content": "Thank you for watching!",
        "duration": 3.0
    })
    
    # Generate audio if requested
    audio_path = None
    if include_audio:
        from app.services.voice_service import generate_speech
        text = summary_obj.summary_text[:3000]
        audio_result = await generate_speech(text, voice_id=voice_id)
        if audio_result["success"]:
            audio_path = audio_result["filepath"]
    
    # Generate video
    result = generate_slideshow_video(
        slides=slides,
        audio_path=audio_path,
        output_filename=f"video_{video_id}.mp4"
    )
    
    if result["success"]:
        return {
            "success": True,
            "filename": result["filename"],
            "filepath": result["filepath"],
            "duration_seconds": result["duration_seconds"],
            "download_url": f"/api/content/video/download/{result['filename']}"
        }
    else:
        raise HTTPException(500, f"Video generation failed: {result['error']}")


@router.get("/video/download/{filename}")
async def download_video(filename: str):
    """Download generated video file."""
    from app.services.video_generator import VIDEO_DIR
    
    filepath = VIDEO_DIR / filename
    if not filepath.exists():
        raise HTTPException(404, "File not found")
    
    return FileResponse(
        str(filepath),
        media_type="video/mp4",
        filename=filename
    )


# ============== Status Endpoint ==============

@router.get("/status")
async def get_phase3_status():
    """Get overall Phase 3 content generation status."""
    from app.services.video_generator import get_video_status
    from app.services.voice_service import get_available_voices
    from app.config import settings
    
    video_status = get_video_status()
    
    return {
        "phase": 3,
        "name": "Content Generation",
        "modules": {
            "script": {
                "available": True,
                "tool": "Groq LLM",
                "status": "ready"
            },
            "slides": {
                "available": True,
                "tool": "python-pptx",
                "status": "ready"
            },
            "images": {
                "available": True,
                "tool": "Unsplash API",
                "status": "ready (uses placeholders if no API key)"
            },
            "voice": {
                "available": bool(getattr(settings, 'ELEVENLABS_API_KEY', None)),
                "tool": "ElevenLabs",
                "status": "ready" if getattr(settings, 'ELEVENLABS_API_KEY', None) else "needs API key"
            },
            "video": {
                "available": video_status["available"],
                "tool": "MoviePy",
                "status": video_status["message"]
            }
        }
    }
