"""Recommendations router - AI-powered video recommendations using embeddings."""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import numpy as np

from app.database import get_db
from app.models.db_models import Video, Summary, Transcript
from app.services.vector_store import get_vector_store
from app.services.embeddings import generate_embedding, create_video_text, compute_similarity
from app.services.youtube_search import search_videos


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


# ============== Global YouTube Recommendations ==============

class GlobalRecommendationResult(BaseModel):
    """A recommendation from global YouTube search."""
    video_id: str
    title: str
    channel_name: str
    description: str
    thumbnail_url: str
    published_at: str
    similarity_score: float


class GlobalRecommendationsResponse(BaseModel):
    """Response with global YouTube recommendations."""
    source_video_id: Optional[str] = None
    source_script: Optional[str] = None
    recommendations: List[GlobalRecommendationResult]
    search_query: str
    total_searched: int


@router.get("/global/{video_id}", response_model=GlobalRecommendationsResponse)
async def get_global_recommendations(
    video_id: str,
    k: int = Query(default=5, ge=1, le=10, description="Number of recommendations"),
    db: Session = Depends(get_db)
):
    """
    Get recommendations from global YouTube based on video content.
    
    This searches YouTube globally versus the script/content of the video,
    then uses embedding similarity to rank the most relevant results.
    """
    # Get video content
    video = db.query(Video).filter(Video.video_id == video_id).first()
    summary = db.query(Summary).filter(Summary.video_id == video_id).first()
    transcript = db.query(Transcript).filter(Transcript.video_id == video_id).first()
    
    if not summary and not transcript:
        raise HTTPException(
            404, 
            "No content found for this video. Generate summary/transcript first."
        )
    
    title = video.title if video else ""
    content = summary.summary_text if summary else ""
    transcript_text = transcript.content if transcript else ""
    
    # Create source embedding from the video's content
    source_text = create_video_text(title, "", content, transcript_text)
    source_embedding = generate_embedding(source_text)
    
    # Extract keywords for YouTube search
    search_query = _extract_search_query(title, content)
    
    # Search YouTube globally
    youtube_results = search_videos(search_query, max_results=20)
    
    if not youtube_results:
        return GlobalRecommendationsResponse(
            source_video_id=video_id,
            recommendations=[],
            search_query=search_query,
            total_searched=0
        )
    
    # Generate embeddings for YouTube results and compare
    ranked_results = []
    
    for yt_video in youtube_results:
        # Skip the same video
        if yt_video["video_id"] == video_id:
            continue
        
        # Create embedding from YouTube video metadata
        yt_text = create_video_text(
            yt_video["title"],
            yt_video["description"],
            "",  # No summary available
            ""   # No transcript available
        )
        yt_embedding = generate_embedding(yt_text)
        
        # Compute similarity
        similarity = compute_similarity(source_embedding, yt_embedding)
        
        ranked_results.append({
            **yt_video,
            "similarity_score": float(similarity)
        })
    
    # Sort by similarity (highest first)
    ranked_results.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    # Take top k results
    top_results = ranked_results[:k]
    
    recommendations = [
        GlobalRecommendationResult(
            video_id=r["video_id"],
            title=r["title"],
            channel_name=r["channel_name"],
            description=r["description"][:200] + "..." if len(r["description"]) > 200 else r["description"],
            thumbnail_url=r["thumbnail_url"],
            published_at=r["published_at"],
            similarity_score=round(r["similarity_score"], 4)
        )
        for r in top_results
    ]
    
    return GlobalRecommendationsResponse(
        source_video_id=video_id,
        recommendations=recommendations,
        search_query=search_query,
        total_searched=len(youtube_results)
    )


@router.post("/global/from-script", response_model=GlobalRecommendationsResponse)
async def get_recommendations_from_script(
    script: str,
    k: int = Query(default=5, ge=1, le=10)
):
    """
    Get global YouTube recommendations based on a script/content.
    
    Searches YouTube and uses embedding similarity to find the most
    relevant videos matching the provided script content.
    """
    if len(script) < 50:
        raise HTTPException(400, "Script must be at least 50 characters")
    
    # Generate embedding for the script
    script_embedding = generate_embedding(script[:2000])
    
    # Extract search query from script
    search_query = _extract_search_query("", script)
    
    # Search YouTube
    youtube_results = search_videos(search_query, max_results=20)
    
    if not youtube_results:
        return GlobalRecommendationsResponse(
            source_script=script[:100] + "...",
            recommendations=[],
            search_query=search_query,
            total_searched=0
        )
    
    # Rank by embedding similarity
    ranked_results = []
    
    for yt_video in youtube_results:
        yt_text = create_video_text(
            yt_video["title"],
            yt_video["description"],
            "", ""
        )
        yt_embedding = generate_embedding(yt_text)
        similarity = compute_similarity(script_embedding, yt_embedding)
        
        ranked_results.append({
            **yt_video,
            "similarity_score": float(similarity)
        })
    
    ranked_results.sort(key=lambda x: x["similarity_score"], reverse=True)
    top_results = ranked_results[:k]
    
    recommendations = [
        GlobalRecommendationResult(
            video_id=r["video_id"],
            title=r["title"],
            channel_name=r["channel_name"],
            description=r["description"][:200] + "..." if len(r["description"]) > 200 else r["description"],
            thumbnail_url=r["thumbnail_url"],
            published_at=r["published_at"],
            similarity_score=round(r["similarity_score"], 4)
        )
        for r in top_results
    ]
    
    return GlobalRecommendationsResponse(
        source_script=script[:100] + "...",
        recommendations=recommendations,
        search_query=search_query,
        total_searched=len(youtube_results)
    )


def _extract_search_query(title: str, content: str) -> str:
    """Extract key search terms from content for YouTube search."""
    import re
    
    # Combine title and content
    full_text = f"{title} {content}"
    
    # Remove common words and extract key terms
    stopwords = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'shall', 'to', 'of', 'in', 'for',
        'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'between', 'under', 'again',
        'further', 'then', 'once', 'and', 'but', 'if', 'or', 'because',
        'until', 'while', 'this', 'that', 'these', 'those', 'it', 'its',
        'they', 'them', 'their', 'what', 'which', 'who', 'whom', 'when',
        'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
        'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
        'same', 'so', 'than', 'too', 'very', 'just', 'also', 'now', 'here',
        'there', 'can', 'about', 'like', 'your', 'you', 'we', 'our', 'i', 'me'
    }
    
    # Tokenize and filter
    words = re.findall(r'\b[a-zA-Z]{3,}\b', full_text.lower())
    keywords = [w for w in words if w not in stopwords]
    
    # Get most frequent keywords
    from collections import Counter
    word_counts = Counter(keywords)
    top_keywords = [word for word, count in word_counts.most_common(5)]
    
    return " ".join(top_keywords) if top_keywords else title[:50]
