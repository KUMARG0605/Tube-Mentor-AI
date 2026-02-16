"""Voice Service - Text-to-Speech using ElevenLabs API."""

import httpx
from pathlib import Path
from typing import Optional, List
import uuid

from app.config import settings

ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"

# Output directory for audio files
AUDIO_DIR = settings.OUTPUT_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Default voices (ElevenLabs pre-made voices)
DEFAULT_VOICES = {
    "rachel": "21m00Tcm4TlvDq8ikWAM",  # American female
    "adam": "pNInz6obpgDQGcFmaJgB",     # American male
    "josh": "TxGEqnHWrfWFTfGW9XjX",     # American male (young)
    "bella": "EXAVITQu4vr4xnSDxMaL",    # American female
    "antoni": "ErXwobaYiN019PkySvjV",   # American male
    "elli": "MF3mGyEYCl7XYWbV9V6O",     # American female (young)
    "sam": "yoZ06aMxZJJ28mfd3POQ",      # American male (narrative)
}


async def get_available_voices() -> List[dict]:
    """Get list of available voices from ElevenLabs."""
    api_key = getattr(settings, 'ELEVENLABS_API_KEY', None)
    
    if not api_key:
        # Return default voice options
        return [
            {"voice_id": vid, "name": name.title(), "available": False}
            for name, vid in DEFAULT_VOICES.items()
        ]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ELEVENLABS_API_URL}/voices",
                headers={"xi-api-key": api_key},
                timeout=10.0
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            voices = []
            for voice in data.get("voices", []):
                voices.append({
                    "voice_id": voice["voice_id"],
                    "name": voice["name"],
                    "category": voice.get("category", ""),
                    "description": voice.get("description", ""),
                    "labels": voice.get("labels", {}),
                    "available": True,
                })
            
            return voices
    except Exception as e:
        print(f"Error fetching voices: {e}")
        return []


async def generate_speech(
    text: str,
    voice_id: str = None,
    model_id: str = "eleven_monolingual_v1",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    output_format: str = "mp3_44100_128"
) -> dict:
    """Convert text to speech using ElevenLabs API.
    
    Args:
        text: Text to convert to speech
        voice_id: ElevenLabs voice ID (defaults to 'rachel')
        model_id: TTS model to use
        stability: Voice stability (0-1)
        similarity_boost: Voice clarity (0-1)
        output_format: Audio format
    
    Returns:
        dict with audio file path and metadata
    """
    api_key = getattr(settings, 'ELEVENLABS_API_KEY', None)
    
    if not api_key:
        return {
            "success": False,
            "error": "ElevenLabs API key not configured. Add ELEVENLABS_API_KEY to .env",
            "filepath": None,
        }
    
    # Use default voice if none provided
    if not voice_id:
        voice_id = DEFAULT_VOICES["rachel"]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ELEVENLABS_API_URL}/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": api_key,
                    "Content-Type": "application/json",
                    "Accept": "audio/mpeg",
                },
                json={
                    "text": text,
                    "model_id": model_id,
                    "voice_settings": {
                        "stability": stability,
                        "similarity_boost": similarity_boost,
                    }
                },
                timeout=60.0  # Longer timeout for audio generation
            )
            
            if response.status_code != 200:
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", {}).get("message", response.text)
                except:
                    pass
                
                return {
                    "success": False,
                    "error": f"ElevenLabs API error: {error_msg}",
                    "filepath": None,
                }
            
            # Save audio file
            filename = f"speech_{uuid.uuid4().hex[:8]}.mp3"
            filepath = AUDIO_DIR / filename
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Estimate duration (rough: ~150 words per minute)
            word_count = len(text.split())
            estimated_duration = (word_count / 150) * 60  # seconds
            
            return {
                "success": True,
                "filename": filename,
                "filepath": str(filepath),
                "word_count": word_count,
                "estimated_duration_seconds": round(estimated_duration, 1),
                "voice_id": voice_id,
            }
            
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Request timed out. Try with shorter text.",
            "filepath": None,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating speech: {str(e)}",
            "filepath": None,
        }


async def generate_script_audio(
    script: str,
    voice_id: str = None,
    chunk_size: int = 5000
) -> dict:
    """Generate audio for a full script, handling long texts by chunking.
    
    ElevenLabs has character limits, so we split long scripts.
    """
    api_key = getattr(settings, 'ELEVENLABS_API_KEY', None)
    
    if not api_key:
        return {
            "success": False,
            "error": "ElevenLabs API key not configured",
            "audio_files": [],
        }
    
    # Split script into chunks
    chunks = []
    current_chunk = ""
    
    sentences = script.replace('\n', ' ').split('. ')
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # Generate audio for each chunk
    audio_files = []
    total_duration = 0
    
    for i, chunk in enumerate(chunks):
        result = await generate_speech(chunk, voice_id=voice_id)
        
        if result["success"]:
            audio_files.append({
                "part": i + 1,
                "filename": result["filename"],
                "filepath": result["filepath"],
                "duration_seconds": result["estimated_duration_seconds"],
            })
            total_duration += result["estimated_duration_seconds"]
        else:
            # Continue even if one chunk fails
            print(f"Chunk {i+1} failed: {result['error']}")
    
    return {
        "success": len(audio_files) > 0,
        "audio_files": audio_files,
        "total_parts": len(chunks),
        "completed_parts": len(audio_files),
        "total_duration_seconds": round(total_duration, 1),
        "voice_id": voice_id or DEFAULT_VOICES["rachel"],
    }


def get_character_count(text: str) -> dict:
    """Get character count info for cost estimation."""
    char_count = len(text)
    
    # ElevenLabs pricing tiers (approximate)
    return {
        "characters": char_count,
        "words": len(text.split()),
        "estimated_cost_usd": round(char_count * 0.00003, 4),  # Rough estimate
        "within_free_tier": char_count <= 10000,
    }
