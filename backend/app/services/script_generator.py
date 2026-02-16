"""Script Generator Service - Create educational scripts using Groq LLM."""

from groq import Groq
from app.config import settings
from typing import Optional

client = Groq(api_key=settings.GROQ_API_KEY)


VIDEO_SCRIPT_PROMPT = """You are an expert educational video script writer.
Based on the following video summary and transcript, create a professional video script that can be used to recreate or explain this content.

VIDEO TITLE: {title}
SUMMARY:
{summary}

TRANSCRIPT EXCERPT:
{transcript}

Create a complete video script with the following structure:

## INTRO (30 seconds)
- Hook/attention grabber
- Brief overview of what viewers will learn

## MAIN CONTENT
- Break down into clear sections with timestamps
- Include talking points for each section
- Add visual cues [SHOW GRAPHIC], [TRANSITION], etc.
- Include examples and explanations

## CONCLUSION (30 seconds)
- Recap key points
- Call to action

## NOTES FOR PRESENTER
- Key emphasis points
- Timing suggestions

Make the script engaging, educational, and suitable for a YouTube video.
Target duration: {duration} minutes.
"""

CUSTOM_SCRIPT_PROMPT = """You are an expert educational video script writer.
Create a professional video script on the following topic:

TOPIC: {topic}
STYLE: {style}
TARGET AUDIENCE: {audience}
DURATION: {duration} minutes

Create a complete video script with the following structure:

## INTRO (30 seconds)
- Hook/attention grabber
- Brief overview of what viewers will learn

## MAIN CONTENT
- Break down into clear sections
- Include talking points for each section
- Add visual cues [SHOW GRAPHIC], [TRANSITION], etc.
- Include examples and explanations

## CONCLUSION (30 seconds)
- Recap key points
- Call to action

## NOTES FOR PRESENTER
- Key emphasis points
- Timing suggestions

Make the script engaging, educational, and professionally structured.
"""


def generate_video_script(
    title: str,
    summary: str,
    transcript: str,
    duration: int = 10
) -> dict:
    """Generate a video script from existing content."""
    
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a professional video script writer."},
            {"role": "user", "content": VIDEO_SCRIPT_PROMPT.format(
                title=title,
                summary=summary,
                transcript=transcript[:10000],
                duration=duration
            )},
        ],
        temperature=0.7,
        max_tokens=4000,
    )
    
    script_content = response.choices[0].message.content
    
    # Estimate word count and duration
    word_count = len(script_content.split())
    estimated_duration = word_count // 150  # ~150 words per minute for speaking
    
    return {
        "title": title,
        "script": script_content,
        "word_count": word_count,
        "estimated_duration_minutes": estimated_duration,
        "target_duration": duration,
    }


def generate_custom_script(
    topic: str,
    style: str = "educational",
    audience: str = "general",
    duration: int = 10
) -> dict:
    """Generate a custom script from scratch on any topic."""
    
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a professional video script writer."},
            {"role": "user", "content": CUSTOM_SCRIPT_PROMPT.format(
                topic=topic,
                style=style,
                audience=audience,
                duration=duration
            )},
        ],
        temperature=0.8,
        max_tokens=4000,
    )
    
    script_content = response.choices[0].message.content
    word_count = len(script_content.split())
    
    return {
        "topic": topic,
        "style": style,
        "audience": audience,
        "script": script_content,
        "word_count": word_count,
        "estimated_duration_minutes": word_count // 150,
        "target_duration": duration,
    }
