"""Quiz service for generating MCQ questions from video transcripts using Groq LLM."""

import json
from groq import Groq
from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

QUIZ_PROMPT = """You are an expert quiz creator for educational content.
Based on the following video transcript titled "{title}", generate exactly {num_questions} multiple-choice quiz questions.

Each question MUST test understanding of the concepts discussed in the video.

Return your response as a valid JSON array with this exact structure:
[
  {{
    "question": "The question text?",
    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
    "correct_answer": "A) Option 1",
    "explanation": "Brief explanation of why this is correct."
  }}
]

Rules:
- Each question must have exactly 4 options (A, B, C, D)
- Questions should range from easy to challenging
- Explanations should be clear and educational
- Return ONLY the JSON array, no other text
- add images to understand better like flow chart and diagrams if needed
TRANSCRIPT:
{transcript}
"""


def generate_quiz(title: str, transcript: str, num_questions: int = 5) -> list[dict]:
    """Generate quiz questions from a video transcript using Groq."""
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {
                "role": "system", 
                "content": "You are a quiz generator. Return only valid JSON."
            },
            {
                "role": "user", 
                "content": QUIZ_PROMPT.format(
                    title=title,
                    num_questions=num_questions,
                    transcript=transcript[:15000],
                )
            },
        ],
        temperature=0.6,
        max_tokens=settings.GROQ_MAX_TOKENS,
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    try:
        questions = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError("Failed to parse quiz questions from LLM response.")

    return questions
