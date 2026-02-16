"""Embeddings service - converts text to vector representations."""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union


_embedding_model = None
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384


def get_embedding_model() -> SentenceTransformer:
    """Get or initialize the embedding model (Singleton pattern)."""
    global _embedding_model
    
    if _embedding_model is None:
        print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print(f"Model loaded! Dimension: {EMBEDDING_DIMENSION}")
    
    return _embedding_model


def generate_embedding(text: Union[str, List[str]]) -> np.ndarray:
    """
    Convert text(s) to embedding vector(s).
    
    Args:
        text: Single string or list of strings
    
    Returns:
        np.ndarray of shape (384,) for single text or (N, 384) for N texts
    """
    model = get_embedding_model()
    
    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    
    return embedding


def compute_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Compute cosine similarity between two embeddings.
    
    Args:
        embedding1: First vector (384,)
        embedding2: Second vector (384,)
    
    Returns:
        float between -1 and 1 (1 = identical, 0 = unrelated, -1 = opposite)
    """
    return float(np.dot(embedding1, embedding2))


def create_video_text(title: str, description: str = "", summary: str = "", transcript: str = "") -> str:
    """
    Combine video metadata into a single text for embedding.
    Prioritizes transcript content for better semantic matching.
    
    Args:
        title: Video title (required)
        description: Video description (optional)
        summary: AI-generated summary (optional)
        transcript: Video transcript content (optional) - KEY for semantic matching
    
    Returns:
        Combined text string for embedding
    """
    parts = [title]
    
    # Include summary if available (concise understanding)
    if summary:
        parts.append(summary[:300])
    
    # Include transcript for actual content-based matching
    # This is the KEY content that makes recommendations relevant
    if transcript:
        # Use meaningful portion of transcript for semantic understanding
        clean_transcript = transcript.replace('\n', ' ').strip()[:800]
        parts.append(clean_transcript)
    elif description:
        # Fallback to description if no transcript
        clean_desc = description.replace('\n', ' ')[:300]
        parts.append(clean_desc)
    
    return " | ".join(parts)
