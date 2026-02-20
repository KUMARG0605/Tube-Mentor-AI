"""Transcript extraction service for YouTube videos."""

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    TranscriptsDisabled,
    # NoTranscriptAvailable,
)


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
        
        # Try requested language first, then fallback to any available
        try:
            fetched = ytt_api.fetch(video_id, languages=[language])
            actual_language = language
        except Exception:
            # Fallback: get list of available transcripts and use first one
            transcript_list = ytt_api.list(video_id)
            available = list(transcript_list)
            if not available:
                raise ValueError(f"No transcripts available for video {video_id}")
            
            # Use the first available transcript
            first_transcript = available[0]
            fetched = first_transcript.fetch()
            actual_language = first_transcript.language_code
        
        full_text = " ".join([entry.text for entry in fetched])

        return {
            "video_id": video_id,
            "language": actual_language,
            "content": full_text,
            "word_count": len(full_text.split()),
        }

    except TranscriptsDisabled:
        raise ValueError(
            f"Subtitles/captions are disabled for this video. "
            f"The video creator has not enabled captions."
        )
    except NoTranscriptFound:
        raise ValueError(
            f"No transcript found in the requested language. "
            f"Try a different video or check if captions are available."
        )
    except NoTranscriptAvailable:
        raise ValueError(
            f"No transcript available for this video. "
            f"The video may not have any captions."
        )
    except VideoUnavailable:
        raise ValueError(
            f"Video is unavailable. It may be private, deleted, or region-restricted."
        )
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Could not fetch transcript for video {video_id}: {str(e)}")
