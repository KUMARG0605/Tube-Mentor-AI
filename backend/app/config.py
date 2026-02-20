"""TubeMentor AI - Configuration Management"""

from pydantic_settings import BaseSettings
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Central configuration class - reads from environment/.env file."""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/tubementor"
    
    # API Keys
    YOUTUBE_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    
    # Phase 3 API Keys (Content Generation)
    UNSPLASH_API_KEY: str = ""       # For image search
    ELEVENLABS_API_KEY: str = ""     # For text-to-speech
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    # Groq LLM Settings
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_TEMPERATURE: float = 0.7
    GROQ_MAX_TOKENS: int = 6000
    
    # YouTube Settings
    YT_MAX_RESULTS: int = 15
    
    # File Paths
    OUTPUT_DIR: Path = Path(__file__).parent.parent / "outputs"
    PDF_DIR: Path = Path(__file__).parent.parent / "outputs" / "pdfs"
    
    class Config:
        env_file = str(PROJECT_ROOT / ".env")
        env_file_encoding = "utf-8"


settings = Settings()

# Create output directories
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
settings.PDF_DIR.mkdir(parents=True, exist_ok=True)
