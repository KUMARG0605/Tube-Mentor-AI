"""Transcript extraction service for YouTube videos."""

from youtube_transcript_api import YouTubeTranscriptApi


def get_transcript(video_id: str, language: str = "en") -> dict:
    """
    Fetch the transcript of a YouTube video.
    
    Args:
        video_id: YouTube video ID (e.g., "dQw4w9WgXcQ")
        language: Language code (default: "en")
    
    Returns:
        Dict with video_id, language, content, and word_count.
    
    Raises:
        ValueError: If transcript is unavailable.
    """
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched = ytt_api.fetch(video_id, languages=[language])
        full_text = " ".join([entry.text for entry in fetched])

        return {
            "video_id": video_id,
            "language": language,
            "content": full_text,
            "word_count": len(full_text.split()),
        }

    except Exception as e:
        raise ValueError(f"Could not fetch transcript for video {video_id}: {str(e)}")
