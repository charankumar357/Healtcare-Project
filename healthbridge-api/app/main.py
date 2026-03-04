"""
HealthBridge AI — FastAPI Application Entry Point
=================================================
Production-ready ASGI app with CORS, router registration,
middleware, and structured logging.

Run: uvicorn app.main:app --reload --port 8000

API Endpoint Map:
  #1  POST /auth/register        — Register ASHA worker
  #2  POST /auth/login           — Login -> JWT
  #3  POST /screening/extract    — Raw text -> extracted symptoms
  #4  POST /screening/score      — Symptoms + demographics -> risk score
  #5  POST /screening/explain    — Score -> plain-language explanation
  #6  POST /screening/recommend  — Tier + symptoms -> recommendation
  #7  POST /screening/complete   — Save completed session to DB
  #8  GET  /screening/sessions   — List sessions for current ASHA
  #9  POST /sessions/sync        — Batch sync offline sessions
  #10 GET  /report/{id}/pdf      — Generate PDF report
  #11 GET  /facilities/nearby    — Google Maps nearby facilities
  #12 POST /audio/transcribe     — Groq Whisper voice-to-text
"""

import logging
import sys
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import check_db_connection

# ─── Structured JSON Logging ───
try:
    from pythonjsonlogger import jsonlogger
    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setFormatter(jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    ))
except ImportError:
    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s"
    ))

logging.root.setLevel(logging.INFO if not settings.debug else logging.DEBUG)
logging.root.addHandler(log_handler)

logger = logging.getLogger("healthbridge")


# ─── Lifespan (startup/shutdown) ───
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"CORS origins: {settings.cors_origins}")

    db_ok = await check_db_connection()
    logger.info(f"Database connection: {'OK' if db_ok else 'FAILED'}")

    yield

    logger.info("Shutting down HealthBridge AI")


# ─── Create FastAPI App ───
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered rural health pre-screening system for India",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── CORS ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Custom Middleware ───
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware

app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RateLimiterMiddleware)

# ─── Register Routers (matches API endpoint map) ───
from app.routers import auth, screening, report, facilities, audio
from app.routers import sessions

app.include_router(auth.router)          # /auth/*
app.include_router(screening.router)     # /screening/*
app.include_router(sessions.router)      # /sessions/*
app.include_router(report.router)        # /report/*
app.include_router(facilities.router)    # /facilities/*
app.include_router(audio.router)         # /audio/*


# ─── Health Check (no auth required) ───
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check — returns app status and DB connectivity."""
    db_ok = await check_db_connection()
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "db": "connected" if db_ok else "disconnected",
        "version": settings.app_version,
    }


@app.get("/", tags=["Health"])
async def root():
    """Root — API info."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }
