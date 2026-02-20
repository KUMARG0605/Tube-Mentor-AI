"""Video Generator Service - Create complete videos with animations, voice, BGM, and captions."""

from pathlib import Path
from typing import List, Optional, Dict
import uuid
import re
import subprocess

from app.config import settings

# Output directories
VIDEO_DIR = settings.OUTPUT_DIR / "videos"
AUDIO_DIR = settings.OUTPUT_DIR / "audio"
VIDEO_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# BGM directory for background music files
BGM_DIR = settings.OUTPUT_DIR / "bgm"
BGM_DIR.mkdir(parents=True, exist_ok=True)

# Check if moviepy is available
try:
    from moviepy import (
        ImageClip, TextClip, AudioFileClip, CompositeVideoClip,
        concatenate_videoclips, ColorClip, CompositeAudioClip,
        VideoFileClip, vfx, concatenate_audioclips
    )
    MOVIEPY_AVAILABLE = True
except ImportError:
    try:
        from moviepy.editor import (
            ImageClip, TextClip, AudioFileClip, CompositeVideoClip,
            concatenate_videoclips, ColorClip, CompositeAudioClip,
            VideoFileClip, vfx, concatenate_audioclips
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
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
            status["ffmpeg_available"] = result.returncode == 0
        except:
            pass
        
        try:
            result = subprocess.run(['magick', '-version'], capture_output=True, timeout=5)
            status["imagemagick_available"] = result.returncode == 0
        except:
            try:
                result = subprocess.run(['convert', '-version'], capture_output=True, timeout=5)
                status["imagemagick_available"] = result.returncode == 0
            except:
                pass
    
    return status


# ============== Animation Functions ==============

def apply_fade_in(clip, duration: float = 0.5):
    """Apply fade-in effect to a clip."""
    if not MOVIEPY_AVAILABLE:
        return clip
    try:
        return clip.with_effects([vfx.CrossFadeIn(duration)])
    except:
        return clip


def apply_fade_out(clip, duration: float = 0.5):
    """Apply fade-out effect to a clip."""
    if not MOVIEPY_AVAILABLE:
        return clip
    try:
        return clip.with_effects([vfx.CrossFadeOut(duration)])
    except:
        return clip


# ============== Caption Generation ==============

def create_caption_clip(
    text: str,
    duration: float,
    size: tuple = (1920, 1080),
    font_size: int = 48,
    position: str = "bottom"
) -> Optional['TextClip']:
    """Create a caption text overlay."""
    if not MOVIEPY_AVAILABLE:
        return None
    
    try:
        txt = TextClip(
            text=text,
            font_size=font_size,
            color='white',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=2,
            size=(size[0] - 200, None),
            method='caption',
            text_align='center'
        ).with_duration(duration)
        
        if position == "bottom":
            txt = txt.with_position(('center', size[1] - 150))
        elif position == "top":
            txt = txt.with_position(('center', 50))
        else:
            txt = txt.with_position('center')
        
        return txt
    except Exception as e:
        print(f"Error creating caption: {e}")
        return None


def generate_captions_from_text(
    text: str,
    total_duration: float,
    words_per_caption: int = 10
) -> List[dict]:
    """Generate timed captions from text."""
    words = text.split()
    captions = []
    
    total_words = len(words)
    time_per_word = total_duration / total_words if total_words > 0 else 0.5
    
    current_time = 0
    for i in range(0, len(words), words_per_caption):
        chunk = words[i:i + words_per_caption]
        caption_text = " ".join(chunk)
        caption_duration = len(chunk) * time_per_word
        
        captions.append({
            "text": caption_text,
            "start": current_time,
            "duration": caption_duration
        })
        current_time += caption_duration
    
    return captions


# ============== Background Music ==============

def get_default_bgm_path() -> Optional[str]:
    """Get path to default background music file."""
    bgm_files = list(BGM_DIR.glob("*.mp3")) + list(BGM_DIR.glob("*.wav"))
    if bgm_files:
        return str(bgm_files[0])
    return None


def add_background_music(video_clip, bgm_path: str, volume: float = 0.15):
    """Add background music to video with appropriate volume."""
    if not MOVIEPY_AVAILABLE or not bgm_path or not Path(bgm_path).exists():
        return video_clip
    
    try:
        bgm = AudioFileClip(bgm_path)
        
        # Loop BGM if shorter than video
        if bgm.duration < video_clip.duration:
            loops_needed = int(video_clip.duration / bgm.duration) + 1
            bgm = concatenate_audioclips([bgm] * loops_needed)
        
        # Trim to video length
        bgm = bgm.subclipped(0, video_clip.duration)
        
        # Lower BGM volume
        bgm = bgm.with_volume_scaled(volume)
        
        # Mix with existing audio
        if video_clip.audio:
            final_audio = CompositeAudioClip([video_clip.audio, bgm])
        else:
            final_audio = bgm
        
        return video_clip.with_audio(final_audio)
    except Exception as e:
        print(f"Error adding BGM: {e}")
        return video_clip


# ============== Main Video Generation ==============

def create_animated_text_clip(
    text: str,
    duration: float = 5.0,
    size: tuple = (1920, 1080),
    font_size: int = 60,
    bg_color: tuple = (15, 23, 42),
    text_color: str = "white",
    animation: str = "fade"
) -> Optional['CompositeVideoClip']:
    """Create an animated text-based video clip."""
    if not MOVIEPY_AVAILABLE:
        return None
    
    try:
        # Background
        bg = ColorClip(size=size, color=bg_color, duration=duration)
        
        # Text overlay
        txt = TextClip(
            text=text,
            font_size=font_size,
            color=text_color,
            font='Arial-Bold',
            size=(size[0] - 100, None),
            method='caption',
            text_align='center'
        ).with_position('center').with_duration(duration)
        
        # Apply animations
        if animation == "fade":
            txt = apply_fade_in(txt, 0.5)
            txt = apply_fade_out(txt, 0.5)
        
        clip = CompositeVideoClip([bg, txt])
        return clip
    except Exception as e:
        print(f"Error creating animated text clip: {e}")
        return None


def create_subscribe_clip(
    duration: float = 5.0,
    size: tuple = (1920, 1080)
) -> Optional['CompositeVideoClip']:
    """Create an animated 'Please Subscribe' ending clip."""
    if not MOVIEPY_AVAILABLE:
        return None
    
    try:
        # Dark background
        bg = ColorClip(size=size, color=(20, 20, 40), duration=duration)
        
        # Main subscribe text
        subscribe_text = TextClip(
            text="Like & Subscribe!",
            font_size=80,
            color='#FF0000',
            font='Arial-Bold',
            stroke_color='white',
            stroke_width=3
        ).with_position(('center', size[1]//2 - 80)).with_duration(duration)
        
        # Bell notification text
        bell_text = TextClip(
            text="Turn on notifications to never miss an update!",
            font_size=40,
            color='white',
            font='Arial'
        ).with_position(('center', size[1]//2 + 30)).with_duration(duration)
        
        # Thank you text
        thanks_text = TextClip(
            text="Thank you for watching!",
            font_size=50,
            color='#00BFFF',
            font='Arial-Bold'
        ).with_position(('center', size[1]//2 + 120)).with_duration(duration)
        
        # Apply animations
        subscribe_text = apply_fade_in(subscribe_text, 0.8)
        bell_text = apply_fade_in(bell_text, 0.5)
        thanks_text = apply_fade_in(thanks_text, 0.5)
        
        clip = CompositeVideoClip([bg, subscribe_text, bell_text, thanks_text])
        clip = apply_fade_out(clip, 1.0)
        
        return clip
    except Exception as e:
        print(f"Error creating subscribe clip: {e}")
        return None


def create_intro_clip(
    title: str,
    duration: float = 6.0,
    size: tuple = (1920, 1080)
) -> Optional['CompositeVideoClip']:
    """Create an animated intro clip with title."""
    if not MOVIEPY_AVAILABLE:
        return None
    
    try:
        # Dark background
        bg = ColorClip(size=size, color=(10, 15, 30), duration=duration)
        
        # Title text
        title_clip = TextClip(
            text=title,
            font_size=70,
            color='white',
            font='Arial-Bold',
            size=(size[0] - 200, None),
            method='caption',
            text_align='center'
        ).with_position('center').with_duration(duration)
        
        title_clip = apply_fade_in(title_clip, 1.0)
        
        # Subtitle
        subtitle = TextClip(
            text="Let's Learn Together!",
            font_size=35,
            color='#00D4FF',
            font='Arial'
        ).with_position(('center', size[1]//2 + 100)).with_duration(duration - 1).with_start(1.0)
        
        subtitle = apply_fade_in(subtitle, 0.5)
        
        clip = CompositeVideoClip([bg, title_clip, subtitle])
        clip = apply_fade_out(clip, 0.5)
        
        return clip
    except Exception as e:
        print(f"Error creating intro clip: {e}")
        return None


async def generate_complete_video(
    script: str,
    title: str,
    voice_text: Optional[str] = None,
    voice_id: Optional[str] = None,
    include_bgm: bool = True,
    include_captions: bool = True,
    output_filename: str = None,
    size: tuple = (1920, 1080),
    fps: int = 24
) -> dict:
    """
    Generate a complete video with:
    - Animated intro
    - Content sections with transitions
    - Voice narration
    - Background music
    - Captions/subtitles
    - Subscribe ending
    
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
        total_duration = 0
        
        # Parse script into sections
        sections = parse_script_sections(script)
        
        # 1. Create Intro Clip
        intro = create_intro_clip(title, duration=6.0, size=size)
        if intro:
            intro = apply_fade_in(intro, 1.0)
            clips.append(intro)
            total_duration += 6.0
        
        # 2. Create Content Section Clips
        section_colors = [
            (25, 35, 55),   # Dark blue
            (35, 25, 45),   # Dark purple
            (25, 45, 35),   # Dark green
            (45, 35, 25),   # Dark orange/brown
            (35, 35, 55),   # Blue-purple
        ]
        
        animations = ["fade", "fade", "fade", "fade", "fade"]
        
        for i, section in enumerate(sections):
            section_title = section.get("title", f"Section {i+1}")
            section_content = section.get("content", "")
            
            color = section_colors[i % len(section_colors)]
            animation = animations[i % len(animations)]
            
            # Title slide for section
            title_clip = create_animated_text_clip(
                section_title,
                duration=4.0,
                size=size,
                font_size=70,
                bg_color=color,
                animation=animation
            )
            
            if title_clip:
                clips.append(title_clip)
                total_duration += 4.0
            
            # Content slide
            if section_content:
                display_content = section_content[:300]
                if len(section_content) > 300:
                    display_content += "..."
                
                content_clip = create_animated_text_clip(
                    display_content,
                    duration=8.0,
                    size=size,
                    font_size=45,
                    bg_color=color,
                    animation="fade"
                )
                
                if content_clip:
                    clips.append(content_clip)
                    total_duration += 8.0
        
        # 3. Create Subscribe Ending
        subscribe = create_subscribe_clip(duration=6.0, size=size)
        if subscribe:
            clips.append(subscribe)
            total_duration += 6.0
        
        if not clips:
            return {
                "success": False,
                "error": "No valid clips created",
                "filepath": None,
            }
        
        # 4. Concatenate all clips
        video = concatenate_videoclips(clips, method="compose")
        
        # 5. Generate Voice Narration
        audio_path = None
        narration_text = voice_text or extract_narration_text(script)
        
        if narration_text:
            from app.services.voice_service import generate_speech
            voice_result = await generate_speech(
                text=narration_text[:5000],
                voice_id=voice_id
            )
            if voice_result.get("success"):
                audio_path = voice_result["filepath"]
        
        # 6. Add Voice Audio
        if audio_path and Path(audio_path).exists():
            try:
                voice_audio = AudioFileClip(audio_path)
                if voice_audio.duration > video.duration:
                    voice_audio = voice_audio.subclipped(0, video.duration)
                video = video.with_audio(voice_audio)
            except Exception as e:
                print(f"Error adding voice: {e}")
        
        # 7. Add Background Music
        if include_bgm:
            bgm_path = get_default_bgm_path()
            if bgm_path:
                video = add_background_music(video, bgm_path, volume=0.1)
        
        # 8. Generate Captions
        if include_captions and narration_text:
            captions = generate_captions_from_text(narration_text, video.duration)
            caption_clips = []
            
            for cap in captions:
                cap_clip = create_caption_clip(
                    cap["text"],
                    cap["duration"],
                    size=size
                )
                if cap_clip:
                    cap_clip = cap_clip.with_start(cap["start"])
                    caption_clips.append(cap_clip)
            
            if caption_clips:
                video = CompositeVideoClip([video] + caption_clips)
        
        # 9. Generate output filename
        if not output_filename:
            output_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
        
        filepath = VIDEO_DIR / output_filename
        
        # 10. Export video
        video.write_videofile(
            str(filepath),
            fps=fps,
            codec='libx264',
            audio_codec='aac',
            bitrate='5000k',
            logger=None
        )
        
        # Cleanup
        video.close()
        for clip in clips:
            try:
                clip.close()
            except:
                pass
        
        return {
            "success": True,
            "filename": output_filename,
            "filepath": str(filepath),
            "duration_seconds": total_duration,
            "resolution": f"{size[0]}x{size[1]}",
            "sections_count": len(sections),
            "has_voice": audio_path is not None,
            "has_bgm": include_bgm,
            "has_captions": include_captions,
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating video: {str(e)}",
            "filepath": None,
        }


def parse_script_sections(script: str) -> List[dict]:
    """Parse a script into sections with titles and content."""
    sections = []
    lines = script.split('\n')
    current_section = {"title": "", "content": ""}
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('## ') or line.startswith('# '):
            if current_section["title"] or current_section["content"]:
                sections.append(current_section)
            current_section = {
                "title": line.lstrip('#').strip(),
                "content": ""
            }
        elif line.startswith('**') and line.endswith('**'):
            if current_section["content"]:
                sections.append(current_section)
            current_section = {
                "title": line.strip('*').strip(),
                "content": ""
            }
        elif line:
            current_section["content"] += line + " "
    
    if current_section["title"] or current_section["content"]:
        sections.append(current_section)
    
    if not sections:
        sections = [{"title": "Content", "content": script[:500]}]
    
    return sections


def extract_narration_text(script: str) -> str:
    """Extract clean text suitable for voice narration from script."""
    text = script.replace('#', '').replace('*', '').replace('_', '')
    text = re.sub(r'\[.*?\]', '', text)
    text = ' '.join(text.split())
    return text


def get_video_status() -> dict:
    """Get status of video generation capabilities."""
    status = check_moviepy()
    
    is_available = status["moviepy_available"] and status["ffmpeg_available"]
    
    if is_available:
        message = "Video generation ready"
    elif status["moviepy_available"] and not status["ffmpeg_available"]:
        message = "FFmpeg not found. Install FFmpeg and add to PATH"
    elif not status["moviepy_available"]:
        message = "MoviePy not installed. Run: pip install moviepy"
    else:
        message = "Install moviepy and ffmpeg for video generation"
    
    return {
        "available": is_available,
        "dependencies": status,
        "output_directory": str(VIDEO_DIR),
        "bgm_directory": str(BGM_DIR),
        "supported_formats": ["mp4", "webm", "avi"] if is_available else [],
        "features": {
            "animations": True,
            "voice_narration": True,
            "background_music": True,
            "captions": True,
            "subscribe_ending": True,
        },
        "message": message
    }


# ============== Legacy Functions ==============

def generate_slideshow_video(
    slides: List[dict],
    audio_path: str = None,
    output_filename: str = None,
    slide_duration: float = 5.0,
    size: tuple = (1920, 1080),
    fps: int = 24
) -> dict:
    """Legacy function - Generate a video from slides with optional audio."""
    if not MOVIEPY_AVAILABLE:
        return {
            "success": False,
            "error": "MoviePy not installed. Install with: pip install moviepy",
            "filepath": None,
        }
    
    try:
        clips = []
        
        for i, slide in enumerate(slides):
            slide_type = slide.get("type", "text")
            content = slide.get("content", "")
            duration = slide.get("duration", slide_duration)
            
            if slide_type == "text":
                clip = create_animated_text_clip(
                    content,
                    duration=duration,
                    size=size,
                    animation="fade"
                )
            elif slide_type == "image":
                clip = create_image_clip(
                    content,
                    duration=duration,
                    size=size
                )
            else:
                continue
            
            if clip:
                clips.append(clip)
        
        # Add subscribe ending
        subscribe = create_subscribe_clip(duration=5.0, size=size)
        if subscribe:
            clips.append(subscribe)
        
        if not clips:
            return {
                "success": False,
                "error": "No valid clips created",
                "filepath": None,
            }
        
        video = concatenate_videoclips(clips, method="compose")
        
        # Add audio
        if audio_path and Path(audio_path).exists():
            try:
                audio = AudioFileClip(audio_path)
                if audio.duration > video.duration:
                    audio = audio.subclipped(0, video.duration)
                video = video.with_audio(audio)
            except Exception as e:
                print(f"Error adding audio: {e}")
        
        # Add BGM
        bgm_path = get_default_bgm_path()
        if bgm_path:
            video = add_background_music(video, bgm_path, volume=0.1)
        
        if not output_filename:
            output_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
        
        filepath = VIDEO_DIR / output_filename
        
        video.write_videofile(
            str(filepath),
            fps=fps,
            codec='libx264',
            audio_codec='aac',
            logger=None
        )
        
        video.close()
        for clip in clips:
            try:
                clip.close()
            except:
                pass
        
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


def create_image_clip(
    image_path: str,
    duration: float = 5.0,
    size: tuple = (1920, 1080)
) -> Optional['ImageClip']:
    """Create a video clip from an image."""
    if not MOVIEPY_AVAILABLE:
        return None
    
    try:
        clip = ImageClip(image_path, duration=duration)
        clip = clip.resized(newsize=size)
        clip = apply_fade_in(clip, 0.5)
        clip = apply_fade_out(clip, 0.5)
        return clip
    except Exception as e:
        print(f"Error creating image clip: {e}")
        return None
