"""Image Service - Fetch relevant images from Unsplash API."""

import httpx
from typing import List, Optional
from app.config import settings

UNSPLASH_API_URL = "https://api.unsplash.com"


async def search_images(
    query: str,
    count: int = 5,
    orientation: str = "landscape"
) -> List[dict]:
    """Search for images on Unsplash.
    
    Args:
        query: Search keywords
        count: Number of images to return (max 30)
        orientation: landscape, portrait, or squarish
    
    Returns:
        List of image data with urls and attribution
    """
    api_key = getattr(settings, 'UNSPLASH_API_KEY', None)
    
    if not api_key:
        # Return placeholder images if no API key
        return get_placeholder_images(query, count)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{UNSPLASH_API_URL}/search/photos",
            params={
                "query": query,
                "per_page": min(count, 30),
                "orientation": orientation,
            },
            headers={
                "Authorization": f"Client-ID {api_key}"
            },
            timeout=10.0
        )
        
        if response.status_code != 200:
            return get_placeholder_images(query, count)
        
        data = response.json()
        
        images = []
        for photo in data.get("results", []):
            images.append({
                "id": photo["id"],
                "description": photo.get("description") or photo.get("alt_description") or query,
                "urls": {
                    "full": photo["urls"]["full"],
                    "regular": photo["urls"]["regular"],
                    "small": photo["urls"]["small"],
                    "thumb": photo["urls"]["thumb"],
                },
                "author": {
                    "name": photo["user"]["name"],
                    "username": photo["user"]["username"],
                    "profile_url": photo["user"]["links"]["html"],
                },
                "download_url": photo["links"]["download"],
                "attribution": f"Photo by {photo['user']['name']} on Unsplash",
            })
        
        return images


async def get_random_images(
    query: str = None,
    count: int = 1,
    topics: List[str] = None
) -> List[dict]:
    """Get random images, optionally filtered by query or topics."""
    api_key = getattr(settings, 'UNSPLASH_API_KEY', None)
    
    if not api_key:
        return get_placeholder_images(query or "abstract", count)
    
    params = {"count": min(count, 30)}
    if query:
        params["query"] = query
    if topics:
        params["topics"] = ",".join(topics)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{UNSPLASH_API_URL}/photos/random",
            params=params,
            headers={
                "Authorization": f"Client-ID {api_key}"
            },
            timeout=10.0
        )
        
        if response.status_code != 200:
            return get_placeholder_images(query or "abstract", count)
        
        photos = response.json()
        if not isinstance(photos, list):
            photos = [photos]
        
        images = []
        for photo in photos:
            images.append({
                "id": photo["id"],
                "description": photo.get("description") or photo.get("alt_description") or "",
                "urls": {
                    "full": photo["urls"]["full"],
                    "regular": photo["urls"]["regular"],
                    "small": photo["urls"]["small"],
                    "thumb": photo["urls"]["thumb"],
                },
                "author": {
                    "name": photo["user"]["name"],
                    "username": photo["user"]["username"],
                    "profile_url": photo["user"]["links"]["html"],
                },
                "download_url": photo["links"]["download"],
                "attribution": f"Photo by {photo['user']['name']} on Unsplash",
            })
        
        return images


def get_placeholder_images(query: str, count: int) -> List[dict]:
    """Return placeholder image data when Unsplash API is unavailable."""
    placeholders = []
    
    # Use placeholder image services
    for i in range(count):
        seed = f"{query}_{i}"
        placeholders.append({
            "id": f"placeholder_{i}",
            "description": f"Placeholder image for {query}",
            "urls": {
                "full": f"https://picsum.photos/seed/{seed}/1920/1080",
                "regular": f"https://picsum.photos/seed/{seed}/1080/720",
                "small": f"https://picsum.photos/seed/{seed}/640/480",
                "thumb": f"https://picsum.photos/seed/{seed}/200/150",
            },
            "author": {
                "name": "Lorem Picsum",
                "username": "picsum",
                "profile_url": "https://picsum.photos",
            },
            "download_url": f"https://picsum.photos/seed/{seed}/1920/1080",
            "attribution": "Placeholder image from Lorem Picsum",
        })
    
    return placeholders


async def download_image(url: str, save_path: str) -> bool:
    """Download an image to a local path."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0, follow_redirects=True)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True
    except Exception as e:
        print(f"Failed to download image: {e}")
    return False


def extract_keywords_for_images(summary: str, max_keywords: int = 5) -> List[str]:
    """Extract relevant keywords from summary for image search.
    
    This is a simple extraction - could be enhanced with NLP.
    """
    # Common words to skip
    stopwords = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
        'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
        'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above',
        'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here',
        'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more',
        'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
        'same', 'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or',
        'because', 'until', 'while', 'this', 'that', 'these', 'those', 'what',
        'which', 'who', 'whom', 'its', 'your', 'their', 'our', 'my', 'his', 'her',
    }
    
    # Extract words, filter, and count
    import re
    words = re.findall(r'\b[a-zA-Z]{4,}\b', summary.lower())
    word_counts = {}
    
    for word in words:
        if word not in stopwords:
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, count in sorted_words[:max_keywords]]
