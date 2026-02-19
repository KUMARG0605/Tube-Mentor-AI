"""YouTube Upload Service - Upload videos using YouTube Data API v3."""

import os
import pickle
import json
from pathlib import Path
from typing import Optional, Dict, List
import httplib2

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False

from app.config import settings

# OAuth scopes required for uploading
SCOPES = ['https://www.googleapis.com/auth/youtube.upload',
          'https://www.googleapis.com/auth/youtube']

# Token storage
TOKEN_DIR = settings.OUTPUT_DIR / "tokens"
TOKEN_DIR.mkdir(parents=True, exist_ok=True)
TOKEN_FILE = TOKEN_DIR / "youtube_token.pickle"
CREDENTIALS_FILE = TOKEN_DIR / "client_secrets.json"

# Valid privacy statuses
VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def check_upload_available() -> dict:
    """Check if YouTube upload is available."""
    return {
        "oauth_available": OAUTH_AVAILABLE,
        "credentials_configured": CREDENTIALS_FILE.exists(),
        "authenticated": TOKEN_FILE.exists(),
        "message": get_status_message()
    }


def get_status_message() -> str:
    """Get human-readable status message."""
    if not OAUTH_AVAILABLE:
        return "Install google-auth-oauthlib: pip install google-auth-oauthlib"
    if not CREDENTIALS_FILE.exists():
        return f"Place client_secrets.json in {TOKEN_DIR}"
    if not TOKEN_FILE.exists():
        return "Authentication required. Call /api/publish/auth to authenticate."
    return "Ready to upload"


def get_authenticated_service():
    """Get authenticated YouTube service."""
    if not OAUTH_AVAILABLE:
        raise Exception("OAuth libraries not installed")
    
    credentials = None
    
    # Load existing token
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'rb') as token:
            credentials = pickle.load(token)
    
    # Refresh or get new credentials
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        elif CREDENTIALS_FILE.exists():
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES)
            credentials = flow.run_local_server(port=8090)
        else:
            raise Exception(f"No client_secrets.json found at {CREDENTIALS_FILE}")
        
        # Save credentials
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(credentials, token)
    
    return build('youtube', 'v3', credentials=credentials)


def get_auth_url() -> dict:
    """Get OAuth authorization URL for manual auth flow."""
    if not OAUTH_AVAILABLE:
        return {"error": "OAuth libraries not installed"}
    
    if not CREDENTIALS_FILE.exists():
        return {"error": f"Place client_secrets.json in {TOKEN_DIR}"}
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE), SCOPES,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        return {
            "auth_url": auth_url,
            "instructions": "Visit this URL, authorize access, then call /api/publish/auth/callback with the code"
        }
    except Exception as e:
        return {"error": str(e)}


def complete_auth(code: str) -> dict:
    """Complete OAuth flow with authorization code."""
    if not OAUTH_AVAILABLE:
        return {"success": False, "error": "OAuth libraries not installed"}
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE), SCOPES,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Save credentials
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(credentials, token)
        
        return {"success": True, "message": "Authentication successful!"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: Optional[List[str]] = None,
    category_id: str = "22",  # People & Blogs
    privacy_status: str = "private",
    thumbnail_path: Optional[str] = None,
    notify_subscribers: bool = True
) -> dict:
    """
    Upload a video to YouTube.
    
    Args:
        video_path: Path to the video file
        title: Video title (max 100 chars)
        description: Video description (max 5000 chars)
        tags: List of tags
        category_id: YouTube category ID
        privacy_status: public, private, or unlisted
        thumbnail_path: Path to custom thumbnail (optional)
        notify_subscribers: Whether to notify subscribers
    
    Returns:
        dict with video ID and URL on success
    """
    if not Path(video_path).exists():
        return {"success": False, "error": f"Video file not found: {video_path}"}
    
    if privacy_status not in VALID_PRIVACY_STATUSES:
        return {"success": False, "error": f"Invalid privacy status: {privacy_status}"}
    
    try:
        youtube = get_authenticated_service()
        
        # Prepare video metadata
        body = {
            'snippet': {
                'title': title[:100],
                'description': description[:5000],
                'tags': tags or [],
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False,
            },
            'notifySubscribers': notify_subscribers
        }
        
        # Create media upload
        media = MediaFileUpload(
            video_path,
            chunksize=1024*1024,  # 1MB chunks
            resumable=True,
            mimetype='video/*'
        )
        
        # Execute upload
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Upload progress: {int(status.progress() * 100)}%")
        
        video_id = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Upload thumbnail if provided
        if thumbnail_path and Path(thumbnail_path).exists():
            try:
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(thumbnail_path)
                ).execute()
            except Exception as e:
                print(f"Thumbnail upload failed: {e}")
        
        return {
            "success": True,
            "video_id": video_id,
            "video_url": video_url,
            "title": title,
            "privacy_status": privacy_status
        }
        
    except HttpError as e:
        error_content = json.loads(e.content.decode('utf-8'))
        error_message = error_content.get('error', {}).get('message', str(e))
        return {"success": False, "error": f"YouTube API error: {error_message}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def update_video_metadata(
    video_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    category_id: Optional[str] = None,
    privacy_status: Optional[str] = None
) -> dict:
    """Update metadata for an existing YouTube video."""
    try:
        youtube = get_authenticated_service()
        
        # Get current video data
        video_response = youtube.videos().list(
            part='snippet,status',
            id=video_id
        ).execute()
        
        if not video_response.get('items'):
            return {"success": False, "error": "Video not found"}
        
        current = video_response['items'][0]
        snippet = current['snippet']
        status = current['status']
        
        # Update fields
        if title:
            snippet['title'] = title[:100]
        if description:
            snippet['description'] = description[:5000]
        if tags is not None:
            snippet['tags'] = tags
        if category_id:
            snippet['categoryId'] = category_id
        if privacy_status and privacy_status in VALID_PRIVACY_STATUSES:
            status['privacyStatus'] = privacy_status
        
        # Execute update
        youtube.videos().update(
            part='snippet,status',
            body={
                'id': video_id,
                'snippet': snippet,
                'status': status
            }
        ).execute()
        
        return {
            "success": True,
            "video_id": video_id,
            "message": "Video metadata updated"
        }
        
    except HttpError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_my_videos(max_results: int = 25) -> dict:
    """Get list of uploaded videos."""
    try:
        youtube = get_authenticated_service()
        
        # Get channel uploads playlist
        channels_response = youtube.channels().list(
            part='contentDetails',
            mine=True
        ).execute()
        
        if not channels_response.get('items'):
            return {"success": False, "error": "No channel found"}
        
        uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Get videos from playlist
        videos_response = youtube.playlistItems().list(
            part='snippet,status',
            playlistId=uploads_playlist_id,
            maxResults=max_results
        ).execute()
        
        videos = []
        for item in videos_response.get('items', []):
            snippet = item['snippet']
            videos.append({
                'video_id': snippet['resourceId']['videoId'],
                'title': snippet['title'],
                'description': snippet['description'][:200],
                'thumbnail_url': snippet['thumbnails'].get('high', {}).get('url', ''),
                'published_at': snippet['publishedAt'],
                'privacy_status': item.get('status', {}).get('privacyStatus', 'unknown')
            })
        
        return {
            "success": True,
            "videos": videos,
            "total": len(videos)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# Category IDs for reference
YOUTUBE_CATEGORIES = {
    "1": "Film & Animation",
    "2": "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "18": "Short Movies",
    "19": "Travel & Events",
    "20": "Gaming",
    "21": "Videoblogging",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "Howto & Style",
    "27": "Education",
    "28": "Science & Technology",
    "29": "Nonprofits & Activism",
}
