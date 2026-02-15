# ============================================================
#        TUBEMENTOR AI — STUDENT LEARNING NOTES
#         "Learn by Building" Progress Tracker
# ============================================================
# Maintained by: KUMAR G
# Started: February 14, 2026
# Tech Stack: FastAPI + ReactJS + PostgreSQL
# ============================================================


# ************************************************************
#                    PROJECT STRUCTURE
# ************************************************************
#
# TubeMentor-AI/
# │
# ├── .env                        ← API keys (NEVER push to GitHub!)
# ├── .gitignore                  ← Files Git should ignore
# │
# ├── backend/                    ← FastAPI (Python backend)
# │   ├── requirements.txt        ← Python packages to install
# │   ├── .env.example            ← Template for .env (safe to share)
# │   └── app/
# │       ├── __init__.py         ← Makes "app" a Python package
# │       ├── main.py             ← FastAPI entry point (starts the server)
# │       ├── config.py           ← Reads .env + stores settings
# │       ├── database.py         ← PostgreSQL connection setup
# │       │
# │       ├── models/             ← "What does the data look like?"
# │       │   ├── db_models.py    ← Database tables (SQLAlchemy ORM)
# │       │   └── schemas.py      ← Request/Response shapes (Pydantic)
# │       │
# │       ├── routers/            ← "What URLs does the API have?"
# │       │   ├── search.py       ← POST /api/search/
# │       │   ├── transcript.py   ← POST /api/transcript/
# │       │   ├── summary.py      ← POST /api/summary/
# │       │   ├── quiz.py         ← POST /api/quiz/
# │       │   └── pdf.py          ← POST /api/pdf/ + GET /download/
# │       │
# │       └── services/           ← "How does the logic actually work?"
# │           ├── youtube_search.py   ← Calls YouTube Data API
# │           ├── transcript.py       ← Extracts video subtitles
# │           ├── summary.py          ← Groq AI summarizes transcript
# │           ├── quiz.py             ← Groq AI generates MCQ quiz
# │           └── pdf_generator.py    ← Builds PDF with ReportLab
# │
# └── frontend/                   ← ReactJS (User Interface)
#     ├── package.json             ← Node.js packages to install
#     ├── vite.config.js           ← Dev server config (proxy to FastAPI)
#     ├── tailwind.config.js       ← Tailwind CSS theme/colors
#     ├── index.html               ← Single HTML page (React mounts here)
#     └── src/
#         ├── main.jsx             ← React entry point
#         ├── App.jsx              ← Routes: / and /video/:id
#         ├── index.css            ← Global styles (Tailwind)
#         ├── services/
#         │   └── api.js           ← Axios calls to FastAPI backend
#         ├── components/
#         │   ├── Navbar.jsx       ← Top navigation bar
#         │   ├── SearchBar.jsx    ← Search input with button
#         │   ├── VideoCard.jsx    ← Video thumbnail card
#         │   ├── QuizCard.jsx     ← Interactive quiz with scoring
#         │   └── LoadingSpinner.jsx
#         └── pages/
#             ├── HomePage.jsx     ← Search page (landing page)
#             └── VideoPage.jsx    ← Video + transcript/summary/quiz/PDF


# ************************************************************
#              CONCEPTS TO LEARN (FOR BEGINNERS)
# ************************************************************
#
# ┌─────────────────────────────────────────────────────────┐
# │  BACKEND CONCEPTS (Python + FastAPI)                    │
# ├─────────────────────────────────────────────────────────┤
# │                                                         │
# │  1. FastAPI Basics                                      │
# │     - What? A Python framework to build REST APIs       │
# │     - File: backend/app/main.py                         │
# │     - Learn: @app.get(), @app.post(), routers           │
# │     - Docs: https://fastapi.tiangolo.com/tutorial/      │
# │                                                         │
# │  2. Pydantic (Data Validation)                          │
# │     - What? Validates request/response data shapes      │
# │     - File: backend/app/models/schemas.py               │
# │     - Learn: BaseModel, type hints, validation          │
# │     - Why? Ensures API receives correct data format     │
# │                                                         │
# │  3. SQLAlchemy ORM (Database)                           │
# │     - What? Python talks to PostgreSQL using classes    │
# │     - File: backend/app/models/db_models.py             │
# │     - File: backend/app/database.py                     │
# │     - Learn: Column, relationship, session, query       │
# │     - Why? Write Python instead of raw SQL              │
# │                                                         │
# │  4. Dependency Injection                                │
# │     - What? FastAPI auto-provides DB sessions to routes │
# │     - File: backend/app/database.py → get_db()          │
# │     - Used in: Every router with Depends(get_db)        │
# │                                                         │
# │  5. Environment Variables                               │
# │     - What? Secret keys stored outside code             │
# │     - File: .env + backend/app/config.py                │
# │     - Why? Never hardcode API keys in source code!      │
# │                                                         │
# └─────────────────────────────────────────────────────────┘
#
# ┌─────────────────────────────────────────────────────────┐
# │  FRONTEND CONCEPTS (ReactJS)                            │
# ├─────────────────────────────────────────────────────────┤
# │                                                         │
# │  1. React Components                                    │usestate: A React Hook that lets you add state to functional components.
# │     - What? Reusable UI building blocks                 │          State is mutable and triggers re-render when updated
# │     - Files: frontend/src/components/*.jsx              │useEffect: A React Hook that lets you perform side effects in functional components.
# │     - Learn: props, useState, useEffect                 │ props :  props are used to pass data from a parent component to a child component
# │                                                         │          Share data and configuration between components
# │  2. React Router                                        │
# │     - What? Navigate between pages without reload       │
# │     - File: frontend/src/App.jsx                        │
# │     - Routes: "/" → HomePage, "/video/:id" → VideoPage  │
# │                                                         │
# │  3. Axios (API Calls)                                   │
# │     - What? Send HTTP requests to FastAPI backend       │
# │     - File: frontend/src/services/api.js                │
# │     - Learn: GET, POST, response handling               │
# │                                                         │
# │  4. Tailwind CSS                                        │
# │     - What? Utility-first CSS (class="bg-red-500")      │
# │     - File: frontend/tailwind.config.js                 │
# │     - Why? Rapid styling without writing CSS files      │
# │                                                         │
# │  5. Vite (Dev Server)                                   │
# │     - What? Fast bundler + dev server for React         │
# │     - File: frontend/vite.config.js                     │
# │     - Feature: Proxy /api → FastAPI at port 8000        │
# │                                                         │
# └─────────────────────────────────────────────────────────┘


# ************************************************************
#           PHASE 1 PROGRESS TRACKER
#         (Task → Files → What It Does)
# ************************************************************
#
# ┌──────┬──────────────────────┬────────────────────────────────────────────┬────────────┐
# │  #   │  TASK                │  FILES INVOLVED                            │  STATUS    │
# ├──────┼──────────────────────┼────────────────────────────────────────────┼────────────┤
# │  1   │  Project Setup       │  .env, .gitignore, requirements.txt,       │  ✅ DONE   │
# │      │                      │  package.json, config.py                   │            │
# ├──────┼──────────────────────┼────────────────────────────────────────────┼────────────┤
# │  2   │  Database Setup      │  backend/app/database.py                   │  ✅ DONE   │
# │      │  (PostgreSQL)        │  backend/app/models/db_models.py           │            │
# │      │                      │  Tables: videos, transcripts,              │            │
# │      │                      │          summaries, quizzes,               │            │
# │      │                      │          search_history                    │            │
# ├──────┼──────────────────────┼────────────────────────────────────────────┼────────────┤
# │  3   │  YouTube Search      │  SERVICE: services/youtube_search.py       │  ✅ DONE   │
# │      │                      │  ROUTER:  routers/search.py               │            │
# │      │                      │  SCHEMA:  schemas.py (SearchRequest/Resp)  │            │
# │      │                      │  API:     POST /api/search/               │            │
# ├──────┼──────────────────────┼────────────────────────────────────────────┼────────────┤
# │  4   │  Transcript Fetch    │  SERVICE: services/transcript.py           │  ✅ DONE   │
# │      │                      │  ROUTER:  routers/transcript.py            │            │
# │      │                      │  SCHEMA:  schemas.py (TranscriptReq/Resp)  │            │
# │      │                      │  API:     POST /api/transcript/            │            │
# ├──────┼──────────────────────┼────────────────────────────────────────────┼────────────┤
# │  5   │  AI Summary          │  SERVICE: services/summary.py              │  ✅ DONE   │
# │      │  (Groq LLM)          │  ROUTER:  routers/summary.py              │            │
# │      │                      │  SCHEMA:  schemas.py (SummaryReq/Resp)     │            │
# │      │                      │  API:     POST /api/summary/              │            │
# ├──────┼──────────────────────┼────────────────────────────────────────────┼────────────┤
# │  6   │  AI Quiz             │  SERVICE: services/quiz.py                 │  ✅ DONE   │
# │      │  (Groq LLM)          │  ROUTER:  routers/quiz.py                 │            │
# │      │                      │  SCHEMA:  schemas.py (QuizReq/Resp)        │            │
# │      │                      │  API:     POST /api/quiz/                 │            │
# ├──────┼──────────────────────┼────────────────────────────────────────────┼────────────┤
# │  7   │  PDF Generation      │  SERVICE: services/pdf_generator.py        │  ✅ DONE   │
# │      │  (ReportLab)         │  ROUTER:  routers/pdf.py                  │            │
# │      │                      │  API:     POST /api/pdf/                  │            │
# │      │                      │  API:     GET  /api/pdf/download/{name}   │            │
# ├──────┼──────────────────────┼────────────────────────────────────────────┼────────────┤
# │  8   │  FastAPI Main App    │  backend/app/main.py                       │  ✅ DONE   │
# │      │                      │  - Registers all routers                   │            │
# │      │                      │  - Sets up CORS for React                  │            │
# │      │                      │  - Creates DB tables on startup            │            │
# ├──────┼──────────────────────┼────────────────────────────────────────────┼────────────┤
# │  9   │  React Frontend      │  frontend/src/App.jsx                      │  ✅ DONE   │
# │      │                      │  frontend/src/services/api.js              │            │
# │      │                      │  frontend/src/components/*.jsx             │            │
# │      │                      │  frontend/src/pages/HomePage.jsx           │            │
# │      │                      │  frontend/src/pages/VideoPage.jsx          │            │
# └──────┴──────────────────────┴────────────────────────────────────────────┴────────────┘


# ************************************************************
#              API FLOW (How Data Moves)
# ************************************************************
#
#   User types "Learn LangChain"
#        │
#        ▼
#   ┌─ React HomePage ─┐
#   │  SearchBar.jsx    │──── POST /api/search/ ────► YouTube Data API
#   └──────────────────-┘                              │
#        │                                             ▼
#        │ clicks a video card              Returns 10 videos
#        ▼                                  (stored in PostgreSQL)
#   ┌─ React VideoPage ┐
#   │  iframe player    │
#   │                   │
#   │  [Get Transcript] │──── POST /api/transcript/ ─► youtube-transcript-api
#   │                   │                               │
#   │  [Gen Summary]    │──── POST /api/summary/ ────► Groq LLM (Llama 3.3)
#   │                   │                               │
#   │  [Gen Quiz]       │──── POST /api/quiz/ ───────► Groq LLM (Llama 3.3)
#   │                   │                               │
#   │  [Gen PDF]        │──── POST /api/pdf/ ────────► ReportLab (PDF file)
#   │                   │                               │
#   │  [Download PDF]   │──── GET /api/pdf/download/  ► Downloads .pdf file
#   └───────────────────┘


# ************************************************************
#           ALL PHASES ROADMAP
# ************************************************************
#
# ┌─────────────────────────────────────────────────────────────┐
# │  PHASE 1 — Core Agent                    ✅ COMPLETED       │
# │  Search + Transcript + Summary + Quiz + PDF                │
# ├─────────────────────────────────────────────────────────────┤
# │  PHASE 2 — Intelligence                  ⬜ NOT STARTED     │
# │  Embeddings (SentenceTransformers)                          │
# │  Vector DB (FAISS)                                          │
# │  Smart Video Recommendations (similarity search)           │
# ├─────────────────────────────────────────────────────────────┤
# │  PHASE 3 — Content Generation            ⬜ NOT STARTED     │
# │  Script writing (Groq)                                      │
# │  Slide generation (python-pptx)                             │
# │  Image fetching (Unsplash API)                              │
# │  Voiceover (ElevenLabs)                                     │
# │  Video assembly (MoviePy)                                   │
# ├─────────────────────────────────────────────────────────────┤
# │  PHASE 4 — Publishing Agent              ⬜ NOT STARTED     │
# │  YouTube Upload (YouTube API)                               │
# │  Auto-generated metadata (LLM)                              │
# └─────────────────────────────────────────────────────────────┘


# ************************************************************
#              HOW TO RUN (Step by Step)
# ************************************************************
#
#   STEP 1: Create PostgreSQL database
#   ─────────────────────────────────────
#   Open pgAdmin or psql and run:
#       CREATE DATABASE tubementor;
#
#   STEP 2: Install & run backend
#   ─────────────────────────────────────
#       cd backend
#       pip install -r requirements.txt
#       uvicorn app.main:app --reload
#       # Opens at http://localhost:8000
#       # API docs at http://localhost:8000/docs
#
#   STEP 3: Install & run frontend
#   ─────────────────────────────────────
#       cd frontend
#       npm install
#       npm run dev
#       # Opens at http://localhost:5173
#
#   STEP 4: Use the app
#   ─────────────────────────────────────
#       1. Go to http://localhost:5173
#       2. Search for any topic
#       3. Click a video
#       4. Transcript loads automatically
#       5. Click "Generate Summary"
#       6. Click "Generate Quiz"
#       7. Click "Generate PDF" → Download!


# ************************************************************
#              MY NOTES (Add your learnings here!)
# ************************************************************
#
# Date: ___________
# What I learned today:
#
#
# Date: ___________
# What I learned today:
#
#
# Date: ___________
# Errors I faced & how I fixed them:
#
#
