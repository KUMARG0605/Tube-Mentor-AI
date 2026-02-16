"""Recommendations router - AI-powered video recommendations using embeddings."""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Video, Summary, Transcript
from app.services.vector_store import get_vector_store
from app.services.embeddings import generate_embedding, create_video_text


router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


class IndexVideoRequest(BaseModel):
    """Request body for adding a video to the index."""
    video_id: str
    title: Optional[str] = None
    description: Optional[str] = ""
    summary: Optional[str] = ""
    thumbnail_url: Optional[str] = ""
    channel_name: Optional[str] = ""


class RecommendationResult(BaseModel):
    """A single recommendation result."""
    video_id: str
    title: str
    similarity_score: float
    thumbnail_url: Optional[str] = ""
    channel_name: Optional[str] = ""


class RecommendationsResponse(BaseModel):
    """Response containing list of recommendations."""
    query_video_id: Optional[str] = None
    query_text: Optional[str] = None
    recommendations: List[RecommendationResult]
    total_indexed: int


class IndexStatsResponse(BaseModel):
    """Statistics about the recommendation index."""
    total_videos: int
    index_size_mb: float
    embedding_dimension: int


@router.post("/index", response_model=dict)
async def index_video(request: IndexVideoRequest, db: Session = Depends(get_db)):
    """Add a video to the recommendation index. Uses TRANSCRIPT for content matching."""
    store = get_vector_store()
    
    # Get video info from DB if not provided
    title = request.title or ""
    description = request.description or ""
    summary_text = request.summary or ""
    thumbnail_url = request.thumbnail_url or ""
    channel_name = request.channel_name or ""
    transcript_text = ""  # KEY: Transcript for content-based matching
    
    if not title:
        # Fetch from database
        video = db.query(Video).filter(Video.video_id == request.video_id).first()
        if video:
            title = str(video.title)
            thumbnail_url = str(video.thumbnail_url or "") or thumbnail_url
            channel_name = str(video.channel_name or "") or channel_name
        else:
            title = f"Video {request.video_id}"
    
    if not summary_text:
        summary_obj = db.query(Summary).filter(Summary.video_id == request.video_id).first()
        if summary_obj:
            summary_text = str(summary_obj.summary_text or "")
    
    # Always fetch transcript - it's the KEY content for similarity!
    transcript = db.query(Transcript).filter(Transcript.video_id == request.video_id).first()
    if transcript:
        transcript_text = str(transcript.content or "")
    
    # Create embedding from title + summary + TRANSCRIPT (content-based)
    text = create_video_text(
        str(title), 
        str(description), 
        str(summary_text),
        transcript_text  # This is the key content!
    )
    embedding = generate_embedding(text)
    
    added = store.add_video(
        video_id=request.video_id,
        title=str(title),
        embedding=embedding,
        description=str(description),
        summary=str(summary_text),
        thumbnail_url=str(thumbnail_url),
        channel_name=str(channel_name),
    )
    
    if added:
        return {
            "success": True,
            "video_id": request.video_id,
            "message": "Video added to recommendation index",
            "total_indexed": store.get_video_count()
        }
    else:
        return {
            "success": False,
            "video_id": request.video_id,
            "message": "Video already in index",
            "total_indexed": store.get_video_count()
        }


@router.get("/similar/{video_id}", response_model=RecommendationsResponse)
async def get_similar_videos(
    video_id: str,
    k: int = Query(default=5, ge=1, le=20, description="Number of recommendations")
):
    """Get videos similar to a specific video."""
    store = get_vector_store()
    
    if not store.has_video(video_id):
        raise HTTPException(
            status_code=404,
            detail=f"Video {video_id} not found in recommendation index. "
                   f"Index the video first using POST /api/recommendations/index"
        )
    
    results = store.search_similar(
        video_id=video_id,
        k=k,
        exclude_video_ids=[video_id]
    )
    
    recommendations = [
        RecommendationResult(
            video_id=vid,
            title=meta.get('title', 'Unknown'),
            similarity_score=round(score, 4),
            thumbnail_url=meta.get('thumbnail_url', ''),
            channel_name=meta.get('channel_name', ''),
        )
        for vid, score, meta in results
    ]
    
    return RecommendationsResponse(
        query_video_id=video_id,
        recommendations=recommendations,
        total_indexed=store.get_video_count()
    )


@router.get("/search", response_model=RecommendationsResponse)
async def semantic_search(
    q: str = Query(..., min_length=2, description="Search query"),
    k: int = Query(default=10, ge=1, le=50, description="Number of results")
):
    """Search for videos using semantic similarity."""
    store = get_vector_store()
    
    if store.get_video_count() == 0:
        return RecommendationsResponse(
            query_text=q,
            recommendations=[],
            total_indexed=0
        )
    
    results = store.search_similar(query=q, k=k)
    
    recommendations = [
        RecommendationResult(
            video_id=vid,
            title=meta.get('title', 'Unknown'),
            similarity_score=round(score, 4),
            thumbnail_url=meta.get('thumbnail_url', ''),
            channel_name=meta.get('channel_name', ''),
        )
        for vid, score, meta in results
    ]
    
    return RecommendationsResponse(
        query_text=q,
        recommendations=recommendations,
        total_indexed=store.get_video_count()
    )


@router.get("/stats", response_model=IndexStatsResponse)
async def get_index_stats():
    """Get statistics about the recommendation index."""
    store = get_vector_store()
    from app.services.embeddings import EMBEDDING_DIMENSION
    
    num_videos = store.get_video_count()
    index_size_bytes = num_videos * EMBEDDING_DIMENSION * 4
    metadata_size_bytes = num_videos * 500
    total_size_mb = (index_size_bytes + metadata_size_bytes) / (1024 * 1024)
    
    return IndexStatsResponse(
        total_videos=num_videos,
        index_size_mb=round(total_size_mb, 2),
        embedding_dimension=EMBEDDING_DIMENSION
    )


@router.post("/index-all", response_model=dict)
async def index_all_videos():
    """Index all videos from the database that have transcripts."""
    from app.database import SessionLocal
    from app.models.db_models import Video, Summary, Transcript
    
    store = get_vector_store()
    db = SessionLocal()
    
    try:
        # Get videos with transcripts (transcript = actual content)
        videos = db.query(Video).join(Transcript).all()
        
        indexed = 0
        skipped = 0
        
        for video in videos:
            vid_id = str(video.video_id)
            if store.has_video(vid_id):
                skipped += 1
                continue
            
            # Get transcript content - KEY for content-based matching
            transcript_text = ""
            transcript = db.query(Transcript).filter(Transcript.video_id == vid_id).first()
            if transcript:
                transcript_text = str(transcript.content or "")
            
            summary_text = ""
            summary = db.query(Summary).filter(Summary.video_id == vid_id).first()
            if summary:
                summary_text = str(summary.summary_text or "")
            
            text = create_video_text(
                str(video.title),
                str(video.description or ""),
                summary_text,
                transcript_text  # Include transcript!
            )
            embedding = generate_embedding(text)
            
            store.add_video(
                video_id=vid_id,
                title=str(video.title),
                embedding=embedding,
                description=str(video.description or ""),
                summary=summary_text,
                thumbnail_url=str(video.thumbnail_url or ""),
                channel_name=str(video.channel_name or ""),
            )
            indexed += 1
        
        return {
            "indexed": indexed,
            "skipped": skipped,
            "total_in_db": len(videos),
            "total_in_index": store.get_video_count()
        }
    
    finally:
        db.close()
