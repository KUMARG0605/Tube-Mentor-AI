"""Search router for YouTube video search endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import SearchRequest, SearchResponse, VideoResult
from app.models.db_models import SearchHistory, Video
from app.services.youtube_search import search_videos

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.post("/", response_model=SearchResponse)
def search_youtube(req: SearchRequest, db: Session = Depends(get_db)):
    """Search YouTube videos and save results to database."""
    try:
        results = search_videos(req.query, req.max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"YouTube search failed: {str(e)}")

    history = SearchHistory(
        query=req.query,
        results_count=len(results),
        results_data=results,
    )
    db.add(history)

    for v in results:
        existing = db.query(Video).filter(Video.video_id == v["video_id"]).first()
        if not existing:
            db.add(Video(
                video_id=v["video_id"],
                title=v["title"],
                channel_name=v["channel_name"],
                description=v["description"],
                thumbnail_url=v["thumbnail_url"],
                published_at=v["published_at"],
            ))

    db.commit()

    return SearchResponse(
        query=req.query,
        total_results=len(results),
        videos=[VideoResult(**v) for v in results],
    )


@router.get("/history")
def get_search_history(limit: int = 20, db: Session = Depends(get_db)):
    """Get recent search history."""
    history = (
        db.query(SearchHistory)
        .order_by(SearchHistory.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": h.id,
            "query": h.query,
            "results_count": h.results_count,
            "created_at": str(h.created_at),
        }
        for h in history
    ]
#    - .first() or .all() → Execute!
#
# 5. TRANSACTION PATTERN:
#    - db.add(obj) → Stage for insert
#    - db.commit() → Save everything
#    - db.rollback() → Cancel everything (on error)
#
# 6. HTTPEXCEPTION:
#    - Return HTTP errors: raise HTTPException(status_code=404, detail="...")
#    - Common codes: 400 (bad request), 404 (not found), 500 (server error)
#
# ════════════════════════════════════════════════════════════════════════════
