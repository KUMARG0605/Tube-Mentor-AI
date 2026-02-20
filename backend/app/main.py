"""
TubeMentor AI - FastAPI Entry Point

Main application entry point that initializes the FastAPI app,
configures middleware, and registers all routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import search, transcript, summary, quiz, pdf, auth

# Phase 2: Try importing recommendations (optional - requires faiss, sentence-transformers)
PHASE2_ENABLED = False
try:
    from app.routers import recommendations
    PHASE2_ENABLED = True
except ImportError:
    recommendations = None
    print("⚠️ Phase 2 (Recommendations) disabled - install: pip install faiss-cpu sentence-transformers")

# Phase 3: Content Generation (optional - requires python-pptx, moviepy)
PHASE3_ENABLED = False
try:
    from app.routers import content
    PHASE3_ENABLED = True
except ImportError:
    content = None
    print("⚠️ Phase 3 (Content Generation) disabled - install: pip install python-pptx moviepy")

# Phase 4: Publishing Agent (optional - requires google-auth-oauthlib)
PHASE4_ENABLED = False
try:
    from app.routers import publish
    PHASE4_ENABLED = True
except ImportError:
    publish = None
    print("⚠️ Phase 4 (Publishing) disabled - install: pip install google-auth-oauthlib")

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

# Register routers - Phase 1 (Core)
app.include_router(auth.router)  # Authentication
app.include_router(search.router)
app.include_router(transcript.router)
app.include_router(summary.router)
app.include_router(quiz.router)
app.include_router(pdf.router)

# Phase 2 (Intelligence) - optional
if PHASE2_ENABLED and recommendations is not None:
    app.include_router(recommendations.router)

# Phase 3 (Content Generation) - optional
if PHASE3_ENABLED and content is not None:
    app.include_router(content.router)

# Phase 4 (Publishing Agent) - optional
if PHASE4_ENABLED and publish is not None:
    app.include_router(publish.router)


@app.get("/")
def root():
    """Return API information and available endpoints."""
    endpoints = {
        "docs": "/docs",
        "auth": "/api/auth/",
        "search": "/api/search/",
        "transcript": "/api/transcript/",
        "summary": "/api/summary/",
        "quiz": "/api/quiz/",
        "pdf": "/api/pdf/",
    }
    
    if PHASE2_ENABLED:
        endpoints["recommendations"] = "/api/recommendations/"
    
    if PHASE3_ENABLED:
        endpoints["content"] = "/api/content/"
    
    if PHASE4_ENABLED:
        endpoints["publish"] = "/api/publish/"
    
    return {
        "app": "TubeMentor AI",
        "version": "1.0.0",
        "phases": {
            "phase1_core": True,
            "phase2_intelligence": PHASE2_ENABLED,
            "phase3_content": PHASE3_ENABLED,
            "phase4_publishing": PHASE4_ENABLED,
        },
        "endpoints": endpoints,
    }


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring systems."""
    return {
        "status": "healthy",
        "phase2_enabled": PHASE2_ENABLED,
        "phase3_enabled": PHASE3_ENABLED,
        "phase4_enabled": PHASE4_ENABLED
    }
