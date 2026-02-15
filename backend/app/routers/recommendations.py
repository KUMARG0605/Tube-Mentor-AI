"""Recommendations router - AI-powered video recommendations using embeddings."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

from app.services.vector_store import get_vector_store
from app.services.embeddings import generate_embedding, create_video_text


router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


class IndexVideoRequest(BaseModel):
    """Request body for adding a video to the index."""
    video_id: str
    title: str
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
async def index_video(request: IndexVideoRequest):
    """Add a video to the recommendation index."""
    store = get_vector_store()
    
    text = create_video_text(
        request.title,
        request.description or "",
        request.summary or ""
    )
    embedding = generate_embedding(text)
    
    added = store.add_video(
        video_id=request.video_id,
        title=request.title,
        embedding=embedding,
        description=request.description or "",
        summary=request.summary or "",
        thumbnail_url=request.thumbnail_url or "",
        channel_name=request.channel_name or "",
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
    """Index all videos from the database that have summaries."""
    from app.database import SessionLocal
    from app.models.db_models import Video, Summary
    
    store = get_vector_store()
    db = SessionLocal()
    
    try:
        videos = db.query(Video).join(Summary).all()
        
        indexed = 0
        skipped = 0
        
        for video in videos:
            if store.has_video(video.video_id):
                skipped += 1
                continue
            
            summary_text = video.summary.content if video.summary else ""
            
            text = create_video_text(
                video.title,
                video.description or "",
                summary_text
            )
            embedding = generate_embedding(text)
            
            store.add_video(
                video_id=video.video_id,
                title=video.title,
                embedding=embedding,
                description=video.description or "",
                summary=summary_text,
                thumbnail_url=video.thumbnail_url or "",
                channel_name=video.channel_name or "",
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
