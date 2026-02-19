"""Publishing Router - Phase 4 API endpoints for YouTube publishing."""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from pathlib import Path

from app.database import get_db
from app.models.db_models import Video, Summary, Transcript


router = APIRouter(prefix="/api/publish", tags=["Publishing"])


# ============== Request/Response Models ==============

class MetadataRequest(BaseModel):
    """Request to generate video metadata."""
    video_id: Optional[str] = None
    content: Optional[str] = None
    title_hint: Optional[str] = None


class MetadataResponse(BaseModel):
    """Generated metadata response."""
    success: bool
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    category_id: Optional[str] = None
    hashtags: Optional[List[str]] = None
    error: Optional[str] = None


class UploadRequest(BaseModel):
    """Request to upload video to YouTube."""
    video_path: str
    title: str = Field(..., max_length=100)
    description: str = Field(..., max_length=5000)
    tags: List[str] = Field(default=[])
    category_id: str = Field(default="27")  # Education
    privacy_status: str = Field(default="private")
    thumbnail_path: Optional[str] = None


class UploadResponse(BaseModel):
    """Upload response."""
    success: bool
    video_id: Optional[str] = None
    video_url: Optional[str] = None
    title: Optional[str] = None
    privacy_status: Optional[str] = None
    error: Optional[str] = None


class AuthCallbackRequest(BaseModel):
    """OAuth callback request."""
    code: str


class GenerateAndUploadRequest(BaseModel):
    """Request to generate video and upload in one step."""
    video_id: str
    privacy_status: str = Field(default="private")
    voice_id: Optional[str] = None
    include_bgm: bool = True
    auto_generate_metadata: bool = True


# ============== Status Endpoints ==============

@router.get("/status")
async def get_publishing_status():
    """Get publishing module status."""
    from app.services.youtube_upload import check_upload_available
    from app.services.video_generator import get_video_status
    
    upload_status = check_upload_available()
    video_status = get_video_status()
    
    return {
        "phase": 4,
        "name": "Publishing Agent",
        "modules": {
            "video_generation": {
                "available": video_status["available"],
                "features": video_status.get("features", {}),
                "message": video_status["message"]
            },
            "metadata_generation": {
                "available": True,
                "tool": "Groq LLM",
                "features": ["title", "description", "tags", "category", "thumbnails"]
            },
            "youtube_upload": {
                "available": upload_status["authenticated"],
                "oauth_ready": upload_status["oauth_available"],
                "credentials_configured": upload_status["credentials_configured"],
                "message": upload_status["message"]
            }
        }
    }


# ============== Authentication Endpoints ==============

@router.get("/auth")
async def get_auth_url():
    """Get YouTube OAuth authorization URL."""
    from app.services.youtube_upload import get_auth_url
    
    result = get_auth_url()
    if "error" in result:
        raise HTTPException(400, result["error"])
    
    return result


@router.post("/auth/callback")
async def complete_authentication(request: AuthCallbackRequest):
    """Complete OAuth authentication with authorization code."""
    from app.services.youtube_upload import complete_auth
    
    result = complete_auth(request.code)
    if not result["success"]:
        raise HTTPException(400, result["error"])
    
    return result


# ============== Metadata Generation Endpoints ==============

@router.post("/metadata/generate", response_model=MetadataResponse)
async def generate_metadata(
    request: MetadataRequest,
    db: Session = Depends(get_db)
):
    """Generate optimized YouTube metadata using LLM."""
    from app.services.metadata_generator import generate_video_metadata
    
    content = request.content
    title_hint = request.title_hint
    
    # Get content from video if video_id provided
    if request.video_id and not content:
        video = db.query(Video).filter(Video.video_id == request.video_id).first()
        summary = db.query(Summary).filter(Summary.video_id == request.video_id).first()
        transcript = db.query(Transcript).filter(Transcript.video_id == request.video_id).first()
        
        if summary:
            content = summary.summary_text
        elif transcript:
            content = transcript.content[:3000]
        else:
            raise HTTPException(404, "No content found for video. Generate summary first.")
        
        if video and not title_hint:
            title_hint = video.title
    
    if not content:
        raise HTTPException(400, "Either video_id or content is required")
    
    result = generate_video_metadata(content, title_hint)
    
    return MetadataResponse(**result)


@router.post("/metadata/titles")
async def generate_title_variations(
    request: MetadataRequest,
    db: Session = Depends(get_db)
):
    """Generate multiple title options for A/B testing."""
    from app.services.metadata_generator import generate_title_variations
    
    content = request.content
    
    if request.video_id and not content:
        summary = db.query(Summary).filter(Summary.video_id == request.video_id).first()
        if summary:
            content = summary.summary_text
        else:
            raise HTTPException(404, "No content found")
    
    if not content:
        raise HTTPException(400, "Either video_id or content is required")
    
    return generate_title_variations(content)


@router.post("/metadata/description")
async def generate_description(
    title: str,
    request: MetadataRequest,
    db: Session = Depends(get_db)
):
    """Generate optimized video description."""
    from app.services.metadata_generator import generate_description
    
    content = request.content
    
    if request.video_id and not content:
        summary = db.query(Summary).filter(Summary.video_id == request.video_id).first()
        if summary:
            content = summary.summary_text
        else:
            raise HTTPException(404, "No content found")
    
    if not content:
        raise HTTPException(400, "Either video_id or content is required")
    
    return generate_description(title, content)


@router.post("/metadata/seo-check")
async def check_seo(title: str, description: str):
    """Analyze metadata for SEO optimization."""
    from app.services.metadata_generator import optimize_for_seo
    
    return optimize_for_seo(title, description)


@router.post("/metadata/thumbnail-text")
async def generate_thumbnail_text(request: MetadataRequest, db: Session = Depends(get_db)):
    """Generate text suggestions for video thumbnail."""
    from app.services.metadata_generator import generate_thumbnail_text
    
    content = request.content
    
    if request.video_id and not content:
        summary = db.query(Summary).filter(Summary.video_id == request.video_id).first()
        if summary:
            content = summary.summary_text
        else:
            raise HTTPException(404, "No content found")
    
    return generate_thumbnail_text(content)


# ============== Upload Endpoints ==============

@router.post("/upload", response_model=UploadResponse)
async def upload_video(request: UploadRequest):
    """Upload a video to YouTube."""
    from app.services.youtube_upload import upload_video
    
    result = await upload_video(
        video_path=request.video_path,
        title=request.title,
        description=request.description,
        tags=request.tags,
        category_id=request.category_id,
        privacy_status=request.privacy_status,
        thumbnail_path=request.thumbnail_path
    )
    
    return UploadResponse(**result)


@router.get("/videos")
async def get_my_videos(max_results: int = Query(default=25, le=50)):
    """Get list of user's uploaded videos."""
    from app.services.youtube_upload import get_my_videos
    
    return get_my_videos(max_results)


@router.put("/videos/{video_id}")
async def update_video(
    video_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    privacy_status: Optional[str] = None
):
    """Update metadata for an existing YouTube video."""
    from app.services.youtube_upload import update_video_metadata
    
    result = await update_video_metadata(
        video_id=video_id,
        title=title,
        description=description,
        tags=tags,
        privacy_status=privacy_status
    )
    
    if not result["success"]:
        raise HTTPException(400, result["error"])
    
    return result


# ============== Full Pipeline Endpoint ==============

@router.post("/generate-and-upload")
async def generate_and_upload(
    request: GenerateAndUploadRequest,
    db: Session = Depends(get_db)
):
    """
    Complete pipeline: Generate video with animations, voice, BGM, captions,
    then auto-generate metadata and upload to YouTube.
    """
    from app.services.video_generator import generate_complete_video
    from app.services.metadata_generator import generate_video_metadata
    from app.services.youtube_upload import upload_video, check_upload_available
    from app.services.script_generator import generate_video_script
    
    # Check upload availability
    upload_status = check_upload_available()
    if not upload_status["authenticated"]:
        raise HTTPException(
            503, 
            f"YouTube upload not available: {upload_status['message']}"
        )
    
    # Get video content
    video = db.query(Video).filter(Video.video_id == request.video_id).first()
    summary = db.query(Summary).filter(Summary.video_id == request.video_id).first()
    transcript = db.query(Transcript).filter(Transcript.video_id == request.video_id).first()
    
    if not summary:
        raise HTTPException(404, "Summary not found. Generate summary first.")
    
    title = video.title if video else f"Video {request.video_id}"
    
    # Step 1: Generate script from content
    script_result = generate_video_script(
        title=title,
        summary=summary.summary_text,
        transcript=transcript.content if transcript else "",
        duration=10
    )
    
    # Step 2: Generate complete video with all features
    video_result = await generate_complete_video(
        script=script_result["script"],
        title=title,
        voice_id=request.voice_id,
        include_bgm=request.include_bgm,
        include_captions=True
    )
    
    if not video_result["success"]:
        raise HTTPException(500, f"Video generation failed: {video_result['error']}")
    
    # Step 3: Generate metadata
    if request.auto_generate_metadata:
        metadata = generate_video_metadata(
            content=summary.summary_text,
            title_hint=title
        )
        
        if not metadata.get("success"):
            # Fallback to basic metadata
            metadata = {
                "title": title[:100],
                "description": summary.summary_text[:500],
                "tags": [],
                "category_id": "27"
            }
    else:
        metadata = {
            "title": title[:100],
            "description": summary.summary_text[:500],
            "tags": [],
            "category_id": "27"
        }
    
    # Step 4: Upload to YouTube
    upload_result = await upload_video(
        video_path=video_result["filepath"],
        title=metadata.get("title", title)[:100],
        description=metadata.get("description", "")[:5000],
        tags=metadata.get("tags", []),
        category_id=metadata.get("category_id", "27"),
        privacy_status=request.privacy_status
    )
    
    return {
        "pipeline_success": upload_result["success"],
        "video_generation": {
            "success": True,
            "filepath": video_result["filepath"],
            "duration": video_result["duration_seconds"],
            "features": {
                "has_voice": video_result.get("has_voice"),
                "has_bgm": video_result.get("has_bgm"),
                "has_captions": video_result.get("has_captions")
            }
        },
        "metadata": {
            "title": metadata.get("title"),
            "description_length": len(metadata.get("description", "")),
            "tags_count": len(metadata.get("tags", []))
        },
        "upload": upload_result
    }


@router.get("/categories")
async def get_youtube_categories():
    """Get list of YouTube video categories."""
    from app.services.youtube_upload import YOUTUBE_CATEGORIES
    
    return {
        "categories": [
            {"id": k, "name": v} for k, v in YOUTUBE_CATEGORIES.items()
        ]
    }
