"""Metadata Generator Service - LLM-powered YouTube metadata generation."""

from groq import Groq
from typing import List, Optional
import json
import re

from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


METADATA_PROMPT = """You are a YouTube SEO expert. Generate optimized metadata for a video.

VIDEO SCRIPT/CONTENT:
{content}

Generate the following in JSON format:
{{
    "title": "Catchy, SEO-optimized title (max 60 chars, include main keyword)",
    "description": "Detailed description with keywords, timestamps, and call-to-action (500-1000 chars)",
    "tags": ["list", "of", "relevant", "tags", "max", "15", "tags"],
    "category": "Best YouTube category from: Education, Science & Technology, Entertainment, Howto & Style, People & Blogs",
    "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"]
}}

Guidelines:
- Title: Include main keyword early, be catchy and specific
- Description: Start with hook, include keywords naturally, add call-to-action
- Tags: Mix broad and specific keywords (5-15 tags)
- Include relevant emoji in title/description where appropriate

Return ONLY valid JSON, no extra text.
"""


TITLE_VARIATIONS_PROMPT = """Generate 5 alternative video titles for this content.
The titles should be catchy, SEO-optimized, and under 60 characters each.

CONTENT SUMMARY:
{content}

Return as JSON array:
["Title 1", "Title 2", "Title 3", "Title 4", "Title 5"]

Make titles diverse - some question-based, some listicle-style, some emotional hooks.
Return ONLY valid JSON array, no extra text.
"""


DESCRIPTION_TEMPLATE = """Generate an optimized YouTube description for this video.

VIDEO TITLE: {title}
VIDEO CONTENT: {content}

Create a description with these sections:
1. HOOK (First 2 lines - most important, appears in search)
2. VIDEO SUMMARY (What the video covers)
3. TIMESTAMPS (If content has clear sections)
4. CALL TO ACTION (Like, Subscribe, Comment)
5. LINKS (Placeholder for social links)
6. HASHTAGS (3-5 relevant hashtags)

Return the complete description text ready to paste into YouTube.
Target length: 500-1500 characters.
"""


def generate_video_metadata(
    content: str,
    title_hint: Optional[str] = None
) -> dict:
    """
    Generate complete YouTube metadata using LLM.
    
    Args:
        content: Video script or summary content
        title_hint: Optional title suggestion
    
    Returns:
        dict with title, description, tags, category, hashtags
    """
    try:
        prompt = METADATA_PROMPT.format(content=content[:3000])
        
        if title_hint:
            prompt += f"\n\nSuggested topic: {title_hint}"
        
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a YouTube SEO expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Clean up response
        result_text = result_text.replace("```json", "").replace("```", "").strip()
        
        # Parse JSON
        metadata = json.loads(result_text)
        
        # Validate and clean
        metadata = {
            "title": str(metadata.get("title", "Untitled Video"))[:100],
            "description": str(metadata.get("description", ""))[:5000],
            "tags": metadata.get("tags", [])[:15],
            "category": str(metadata.get("category", "Education")),
            "hashtags": metadata.get("hashtags", [])[:5],
            "success": True
        }
        
        # Map category to ID
        metadata["category_id"] = get_category_id(metadata["category"])
        
        return metadata
        
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse LLM response: {str(e)}",
            "raw_response": result_text if 'result_text' in locals() else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def generate_title_variations(content: str) -> dict:
    """Generate multiple title options for A/B testing."""
    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": "Return only valid JSON array."},
                {"role": "user", "content": TITLE_VARIATIONS_PROMPT.format(content=content[:2000])}
            ],
            temperature=0.9,
            max_tokens=500,
        )
        
        result_text = response.choices[0].message.content.strip()
        result_text = result_text.replace("```json", "").replace("```", "").strip()
        
        titles = json.loads(result_text)
        
        return {
            "success": True,
            "titles": titles[:5]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def generate_description(
    title: str,
    content: str,
    include_timestamps: bool = True
) -> dict:
    """Generate an optimized YouTube description."""
    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a YouTube content creator expert."},
                {"role": "user", "content": DESCRIPTION_TEMPLATE.format(
                    title=title,
                    content=content[:3000]
                )}
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        
        description = response.choices[0].message.content.strip()
        
        return {
            "success": True,
            "description": description[:5000]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def generate_tags_from_content(content: str, max_tags: int = 15) -> List[str]:
    """Extract relevant tags from content using LLM."""
    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": "Extract keywords as JSON array. Return ONLY the array."},
                {"role": "user", "content": f"Extract {max_tags} relevant YouTube tags from this content:\n\n{content[:2000]}"}
            ],
            temperature=0.5,
            max_tokens=300,
        )
        
        result = response.choices[0].message.content.strip()
        result = result.replace("```json", "").replace("```", "").strip()
        
        tags = json.loads(result)
        return tags[:max_tags]
        
    except:
        # Fallback: simple keyword extraction
        words = content.lower().split()
        # Filter common words and get unique keywords
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 
                     'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                     'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
                     'as', 'into', 'through', 'during', 'before', 'after', 'above',
                     'below', 'between', 'under', 'again', 'further', 'then', 'once',
                     'and', 'but', 'if', 'or', 'because', 'until', 'while', 'this',
                     'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their'}
        
        keywords = [w for w in words if len(w) > 3 and w not in stopwords and w.isalpha()]
        unique_keywords = list(dict.fromkeys(keywords))
        return unique_keywords[:max_tags]


def get_category_id(category_name: str) -> str:
    """Map category name to YouTube category ID."""
    categories = {
        "film & animation": "1",
        "autos & vehicles": "2",
        "music": "10",
        "pets & animals": "15",
        "sports": "17",
        "travel & events": "19",
        "gaming": "20",
        "people & blogs": "22",
        "comedy": "23",
        "entertainment": "24",
        "news & politics": "25",
        "howto & style": "26",
        "education": "27",
        "science & technology": "28",
        "nonprofits & activism": "29",
    }
    
    name_lower = category_name.lower()
    for key, value in categories.items():
        if key in name_lower or name_lower in key:
            return value
    
    return "27"  # Default to Education


def optimize_for_seo(title: str, description: str) -> dict:
    """Analyze and suggest SEO improvements."""
    suggestions = []
    score = 100
    
    # Title checks
    if len(title) > 60:
        suggestions.append("Title is too long. Keep under 60 characters for full display.")
        score -= 10
    if len(title) < 30:
        suggestions.append("Title is short. Consider adding more descriptive keywords.")
        score -= 5
    if not any(char.isdigit() for char in title):
        suggestions.append("Consider adding numbers to title (e.g., '5 Tips', '2024 Guide')")
    
    # Description checks
    if len(description) < 200:
        suggestions.append("Description is too short. Add more keywords and details.")
        score -= 15
    if "subscribe" not in description.lower():
        suggestions.append("Add a call-to-action asking viewers to subscribe.")
        score -= 5
    if "#" not in description:
        suggestions.append("Add relevant hashtags at the end of description.")
        score -= 5
    
    return {
        "score": max(0, score),
        "suggestions": suggestions,
        "title_length": len(title),
        "description_length": len(description)
    }


def generate_thumbnail_text(content: str) -> dict:
    """Generate text suggestions for video thumbnail."""
    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a YouTube thumbnail designer."},
                {"role": "user", "content": f"""Generate thumbnail text options for this video content:

{content[:1000]}

Return JSON with:
{{
    "main_text": "Bold, short text (2-4 words max)",
    "subtext": "Optional smaller text",
    "emoji": "1-2 relevant emojis",
    "color_scheme": "suggested colors",
    "alternatives": ["alt1", "alt2", "alt3"]
}}

Return ONLY valid JSON."""}
            ],
            temperature=0.8,
            max_tokens=400,
        )
        
        result = response.choices[0].message.content.strip()
        result = result.replace("```json", "").replace("```", "").strip()
        
        return {
            "success": True,
            **json.loads(result)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
