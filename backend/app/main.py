"""
TubeMentor AI - FastAPI Entry Point

Main application entry point that initializes the FastAPI app,
configures middleware, and registers all routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import search, transcript, summary, quiz, pdf, recommendations

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="TubeMentor AI",
    description="AI-powered YouTube learning assistant — Search, Summarize, Quiz, PDF",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(search.router)
app.include_router(transcript.router)
app.include_router(summary.router)
app.include_router(quiz.router)
app.include_router(pdf.router)
app.include_router(recommendations.router)


@app.get("/")
def root():
    """Return API information and available endpoints."""
    return {
        "app": "TubeMentor AI",
        "version": "1.0.0",
        "phase": "Phase 1 — Core Agent",
        "endpoints": {
            "docs": "/docs",
            "search": "/api/search/",
            "transcript": "/api/transcript/",
            "summary": "/api/summary/",
            "quiz": "/api/quiz/",
            "pdf": "/api/pdf/",
        },
    }


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring systems."""
    return {"status": "healthy"}
