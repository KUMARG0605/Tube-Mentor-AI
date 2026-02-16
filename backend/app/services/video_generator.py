"""Video Generator Service - Create videos using MoviePy."""

from pathlib import Path
from typing import List, Optional
import uuid

from app.config import settings

# Output directory for videos
VIDEO_DIR = settings.OUTPUT_DIR / "videos"
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

# Check if moviepy is available
try:
    from moviepy.editor import (
        ImageClip, TextClip, AudioFileClip, CompositeVideoClip,
        concatenate_videoclips, ColorClip
    )
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False


def check_moviepy() -> dict:
    """Check if MoviePy and required dependencies are available."""
    status = {
        "moviepy_available": MOVIEPY_AVAILABLE,
        "ffmpeg_available": False,
        "imagemagick_available": False,
    }
    
    if MOVIEPY_AVAILABLE:
        try:
            import subprocess
            # Check ffmpeg
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
            status["ffmpeg_available"] = result.returncode == 0
        except:
            pass
        
        try:
            import subprocess
            # Check ImageMagick
            result = subprocess.run(['magick', '-version'], capture_output=True, timeout=5)
            status["imagemagick_available"] = result.returncode == 0
        except:
            try:
                result = subprocess.run(['convert', '-version'], capture_output=True, timeout=5)
                status["imagemagick_available"] = result.returncode == 0
            except:
                pass
    
    return status


def create_text_slide_clip(
    text: str,
    duration: float = 5.0,
    size: tuple = (1920, 1080),
    font_size: int = 60,
    bg_color: tuple = (15, 23, 42),
    text_color: str = "white"
) -> Optional['ImageClip']:
    """Create a text-based video clip (slide)."""
    if not MOVIEPY_AVAILABLE:
        return None
    
    try:
        # Background
        bg = ColorClip(size=size, color=bg_color, duration=duration)
        
        # Text overlay
        txt = TextClip(
            text,
            fontsize=font_size,
            color=text_color,
            font='Arial',
            size=(size[0] - 100, None),
            method='caption',
            align='center'
        ).set_position('center').set_duration(duration)
        
        # Composite
        clip = CompositeVideoClip([bg, txt])
        return clip
    except Exception as e:
        print(f"Error creating text clip: {e}")
        return None


def create_image_clip(
    image_path: str,
    duration: float = 5.0,
    size: tuple = (1920, 1080),
    zoom: bool = False
) -> Optional['ImageClip']:
    """Create a video clip from an image."""
    if not MOVIEPY_AVAILABLE:
        return None
    
    try:
        clip = ImageClip(image_path, duration=duration)
        clip = clip.resize(newsize=size)
        
        if zoom:
            # Ken Burns effect (slight zoom)
            def zoom_effect(get_frame, t):
                zoom_factor = 1 + 0.1 * (t / duration)
                return get_frame(t)
            # Note: Full implementation would use resize during transform
        
        return clip
    except Exception as e:
        print(f"Error creating image clip: {e}")
        return None


def generate_slideshow_video(
    slides: List[dict],
    audio_path: str = None,
    output_filename: str = None,
    slide_duration: float = 5.0,
    size: tuple = (1920, 1080),
    fps: int = 24
) -> dict:
    """Generate a video from slides with optional audio.
    
    Args:
        slides: List of {"type": "text"|"image", "content": str, "duration": float}
        audio_path: Path to audio file (optional)
        output_filename: Output filename (auto-generated if not provided)
        slide_duration: Default duration per slide
        size: Video resolution
        fps: Frames per second
    
    Returns:
        dict with video path and metadata
    """
    if not MOVIEPY_AVAILABLE:
        return {
            "success": False,
            "error": "MoviePy not installed. Install with: pip install moviepy",
            "filepath": None,
        }
    
    try:
        clips = []
        
        for slide in slides:
            slide_type = slide.get("type", "text")
            content = slide.get("content", "")
            duration = slide.get("duration", slide_duration)
            
            if slide_type == "text":
                clip = create_text_slide_clip(
                    content,
                    duration=duration,
                    size=size
                )
            elif slide_type == "image":
                clip = create_image_clip(
                    content,  # image path
                    duration=duration,
                    size=size
                )
            else:
                continue
            
            if clip:
                clips.append(clip)
        
        if not clips:
            return {
                "success": False,
                "error": "No valid clips created",
                "filepath": None,
            }
        
        # Concatenate all clips
        video = concatenate_videoclips(clips, method="compose")
        
        # Add audio if provided
        if audio_path and Path(audio_path).exists():
            try:
                audio = AudioFileClip(audio_path)
                # Match video duration to audio or vice versa
                if audio.duration > video.duration:
                    audio = audio.subclip(0, video.duration)
                video = video.set_audio(audio)
            except Exception as e:
                print(f"Error adding audio: {e}")
        
        # Generate output filename
        if not output_filename:
            output_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
        
        filepath = VIDEO_DIR / output_filename
        
        # Export video
        video.write_videofile(
            str(filepath),
            fps=fps,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        # Cleanup
        video.close()
        for clip in clips:
            clip.close()
        
        return {
            "success": True,
            "filename": output_filename,
            "filepath": str(filepath),
            "duration_seconds": video.duration,
            "resolution": f"{size[0]}x{size[1]}",
            "slides_count": len(clips),
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating video: {str(e)}",
            "filepath": None,
        }


def generate_video_from_script(
    script_sections: List[dict],
    images: List[str] = None,
    audio_path: str = None,
    output_filename: str = None
) -> dict:
    """Generate a complete video from script sections with images and audio.
    
    Args:
        script_sections: List of {"title": str, "content": str}
        images: List of image paths (one per section)
        audio_path: Full narration audio path
        output_filename: Output filename
    
    Returns:
        dict with video path and metadata
    """
    if not MOVIEPY_AVAILABLE:
        return {
            "success": False,
            "error": "MoviePy not installed",
            "filepath": None,
        }
    
    # Calculate duration per section
    total_sections = len(script_sections)
    
    # If we have audio, distribute time across sections
    audio_duration = None
    if audio_path and Path(audio_path).exists():
        try:
            audio = AudioFileClip(audio_path)
            audio_duration = audio.duration
            audio.close()
        except:
            pass
    
    # Default 10 seconds per section, or distribute audio duration
    section_duration = (audio_duration / total_sections) if audio_duration else 10.0
    
    slides = []
    for i, section in enumerate(script_sections):
        # Title slide
        slides.append({
            "type": "text",
            "content": section.get("title", f"Section {i+1}"),
            "duration": 3.0
        })
        
        # Image slide (if available)
        if images and i < len(images) and images[i]:
            slides.append({
                "type": "image",
                "content": images[i],
                "duration": section_duration - 3.0
            })
        else:
            # Content as text
            slides.append({
                "type": "text",
                "content": section.get("content", "")[:200] + "...",
                "duration": section_duration - 3.0
            })
    
    return generate_slideshow_video(
        slides=slides,
        audio_path=audio_path,
        output_filename=output_filename
    )


def get_video_status() -> dict:
    """Get status of video generation capabilities."""
    status = check_moviepy()
    
    return {
        "available": status["moviepy_available"] and status["ffmpeg_available"],
        "dependencies": status,
        "output_directory": str(VIDEO_DIR),
        "supported_formats": ["mp4", "webm", "avi"] if status["moviepy_available"] else [],
        "message": "Video generation ready" if status["moviepy_available"] else "Install moviepy and ffmpeg for video generation"
    }
