"""Summary service - AI-powered video summarization using Groq LLM."""

import json
from groq import Groq
from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

SUMMARY_PROMPT = """You are an expert educational content summarizer.
Given the following transcript of a YouTube video titled "{title}", create a comprehensive summary.

Your summary MUST include:
1. **Overview** - A brief 2-3 sentence overview of the entire video.
2. **Key Topics** - A bullet list of the main topics/concepts covered.
3. **Detailed Notes** - A detailed breakdown of each topic with key points explained clearly.
4. **Key Takeaways** - The most important things to remember.
5. **Examples** - Include relevant examples to illustrate concepts.
Format your response in clean Markdown.

TRANSCRIPT:
{transcript}
"""

KEY_TOPICS_PROMPT = """From the following video transcript, extract just the key topic names as a JSON array of strings.
Return ONLY the JSON array, nothing else.
Example: ["Topic 1", "Topic 2", "Topic 3"]

TRANSCRIPT:
{transcript}
"""


def generate_summary(title: str, transcript: str) -> dict:
    """Generate a structured summary from a video transcript using Groq."""
    
    # Generate main summary
    summary_response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful educational assistant."},
            {"role": "user", "content": SUMMARY_PROMPT.format(
                title=title, 
                transcript=transcript[:15000]
            )},
        ],
        temperature=settings.GROQ_TEMPERATURE,
        max_tokens=settings.GROQ_MAX_TOKENS,
    )
    summary_text = summary_response.choices[0].message.content

    # Extract key topics
    topics_response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You extract key topics as a JSON array."},
            {"role": "user", "content": KEY_TOPICS_PROMPT.format(
                transcript=transcript[:10000]
            )},
        ],
        temperature=0.3,
        max_tokens=500,
    )
    topics_raw = topics_response.choices[0].message.content.strip()

    # Parse topics JSON with fallback
    try:
        key_topics = json.loads(topics_raw)
    except json.JSONDecodeError:
        key_topics = [
            t.strip().strip('"') 
            for t in topics_raw.strip("[]").split(",")
        ]

    return {
        "summary_text": summary_text,
        "key_topics": key_topics,
    }
