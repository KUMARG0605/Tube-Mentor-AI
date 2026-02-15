"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Search Schemas

class SearchRequest(BaseModel):
    """Search request with query and optional max results."""
    query: str
    max_results: int = 10


class VideoResult(BaseModel):
    """Single video in search results."""
    video_id: str
    title: str
    channel_name: str
    description: str
    thumbnail_url: str
    published_at: str

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """Search response containing matched videos."""
    query: str
    total_results: int
    videos: list[VideoResult]


# Transcript Schemas

class TranscriptRequest(BaseModel):
    """Request to fetch video transcript."""
    video_id: str
    language: str = "en"


class TranscriptResponse(BaseModel):
    """Video transcript response."""
    video_id: str
    language: str
    content: str
    word_count: int


# Summary Schemas

class SummaryRequest(BaseModel):
    """Request to generate video summary."""
    video_id: str


class SummaryResponse(BaseModel):
    """AI-generated video summary."""
    video_id: str
    title: str
    summary_text: str
    key_topics: list[str]


# Quiz Schemas

class QuizQuestion(BaseModel):
    """Single quiz question with options and answer."""
    question: str
    options: list[str]
    correct_answer: str
    explanation: str


class QuizRequest(BaseModel):
    """Request to generate quiz."""
    video_id: str
    num_questions: int = 5


class QuizResponse(BaseModel):
    """AI-generated quiz with questions."""
    video_id: str
    title: str
    total_questions: int
    questions: list[QuizQuestion]


# PDF Schemas

class PDFRequest(BaseModel):
    """Request to generate PDF study material."""
    video_id: str
    include_summary: bool = True
    include_quiz: bool = True


class PDFResponse(BaseModel):
    """Generated PDF information."""
    video_id: str
    title: str
    file_name: str
    download_url: str
