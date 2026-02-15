"""
TubeMentor AI - Database Models (ORM)

SQLAlchemy ORM models defining database table structures.
Each class maps to a PostgreSQL table.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class SearchHistory(Base):
    """Stores user search queries for analytics and recommendations."""
    
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(500), nullable=False, index=True)
    results_count = Column(Integer, default=0)
    results_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Video(Base):
    """Main table storing YouTube video metadata."""
    
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    channel_name = Column(String(300), nullable=True)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    duration = Column(String(50), nullable=True)
    view_count = Column(String(50), nullable=True)
    published_at = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships (1-to-1)
    transcript = relationship("Transcript", back_populates="video", uselist=False)
    summary = relationship("Summary", back_populates="video", uselist=False)
    quiz = relationship("Quiz", back_populates="video", uselist=False)


class Transcript(Base):
    """Stores video transcript/subtitle text."""
    
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(20), ForeignKey("videos.video_id"), unique=True, nullable=False)
    language = Column(String(10), default="en")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    video = relationship("Video", back_populates="transcript")


class Summary(Base):
    """Stores AI-generated video summaries."""
    
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(20), ForeignKey("videos.video_id"), unique=True, nullable=False)
    summary_text = Column(Text, nullable=False)
    key_topics = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    video = relationship("Video", back_populates="summary")


class Quiz(Base):
    """Stores AI-generated quiz questions as JSON."""
    
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(20), ForeignKey("videos.video_id"), unique=True, nullable=False)
    questions = Column(JSON, nullable=False)
    total_questions = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    video = relationship("Video", back_populates="quiz")
