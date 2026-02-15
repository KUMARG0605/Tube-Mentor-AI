"""YouTube search service using YouTube Data API v3."""

from googleapiclient.discovery import build
from app.config import settings


def search_videos(query: str, max_results: int = 15) -> list[dict]:
    """Search YouTube videos by query.
    
    Args:
        query: Search term
        max_results: Maximum number of results to return
    
    Returns:
        List of video dictionaries with video_id, title, channel_name,
        description, thumbnail_url, and published_at fields
    """
    youtube = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)

    search_response = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        order="relevance",
        maxResults=max_results,
    ).execute()

    videos = []
    for item in search_response.get("items", []):
        snippet = item["snippet"]
        videos.append({
            "video_id": item["id"]["videoId"],
            "title": snippet["title"],
            "channel_name": snippet["channelTitle"],
            "description": snippet["description"],
            "thumbnail_url": snippet["thumbnails"]["high"]["url"],
            "published_at": snippet["publishedAt"],
        })

    return videos
