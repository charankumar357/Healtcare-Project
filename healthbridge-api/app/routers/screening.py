"""
Screening router — individual pipeline endpoints matching API endpoint map.

#3  POST /screening/extract   — raw text -> extracted symptoms JSON
#4  POST /screening/score     — symptoms + demographics -> risk score + tier
#5  POST /screening/explain   — score + tier -> plain-language explanation
#6  POST /screening/recommend — risk tier + symptoms -> recommendation content
#7  POST /screening/complete  — save full completed session to PostgreSQL
#8  GET  /screening/sessions  — get all sessions for current ASHA worker
"""

import json
import time
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.session import ScreeningSession
from app.models.patient import Patient
from app.models.asha_worker import ASHAWorker
from app.routers.auth import get_current_worker
from app.services.llm_service import LLMService

router = APIRouter(prefix="/screening", tags=["Screening"])


# ═══════════════════════════════════════════════════════════════════════════
# REQUEST / RESPONSE SCHEMAS  (endpoint-specific)
# ═══════════════════════════════════════════════════════════════════════════

class ExtractRequest(BaseModel):
    """POST /screening/extract"""
    symptom_text: str = Field(..., min_length=3, max_length=2000)
    language: str = Field("auto", pattern="^(auto|en|hi|te|ta|kn)$")


class ExtractResponse(BaseModel):
    symptoms: list[dict]
    detected_language: str
    input_quality: str = "clear"
    clarification_needed: list[str] = Field(default_factory=list)


class ScoreRequest(BaseModel):
    """POST /screening/score"""
    symptoms: list[dict] = Field(..., min_length=1)
    demographics: Optional[dict] = None


class ScoreResponse(BaseModel):
    risk_score: int = Field(..., ge=0, le=100)
    risk_tier: str
    top_contributors: list[dict] = Field(default_factory=list)
    red_flag_triggered: bool = False
    red_flag_reason: Optional[str] = None
    recommendation_type: str
    confidence: float = 0.9


class ExplainRequest(BaseModel):
    """POST /screening/explain"""
    risk_score: int
    risk_tier: str
    top_contributors: list[dict] = Field(default_factory=list)
    recommendation_type: str
    language: str = Field("en", pattern="^(en|hi|te|ta|kn)$")


class ExplainResponse(BaseModel):
    explanation_language: str
    score_summary: str
    why_this_score: list[str] = Field(default_factory=list)
    what_it_means: str
    what_to_do_now: str
    urgency_statement: str


class RecommendRequest(BaseModel):
    """POST /screening/recommend"""
    recommendation_type: str = Field(..., pattern="^(self_care|teleconsultation|hospital_visit|emergency)$")
    top_symptoms: list[str] = Field(default_factory=list)
    risk_tier: str
    language: str = Field("en", pattern="^(en|hi|te|ta|kn)$")


class RecommendResponse(BaseModel):
    primary_action: str
    steps: list[str]
    home_care_tips: Optional[list[str]] = None
    warning_signs: list[str] = Field(default_factory=list)
    follow_up: str
    emergency_number: Optional[str] = None
    teleconsult_link: Optional[str] = None
    nearby_facility_search: bool = False


class CompleteSessionRequest(BaseModel):
    """POST /screening/complete"""
    patient_id: Optional[UUID] = None
    symptom_text: str
    language: str = "en"
    input_mode: str = Field("text", pattern="^(text|voice)$")
    # Results from previous pipeline calls
    extraction: dict
    scoring: dict
    explanation: dict
    recommendation: dict
    scoring_method: str = Field("llm", pattern="^(llm|offline)$")
    llm_model_used: Optional[str] = None
    llm_latency_ms: Optional[int] = None


class CompleteSessionResponse(BaseModel):
    session_id: UUID
    risk_score: int
    risk_tier: str
    recommendation_type: str
    created_at: datetime


class SessionListItem(BaseModel):
    id: UUID
    risk_score: Optional[int] = None
    risk_tier: Optional[str] = None
    recommendation_type: Optional[str] = None
    raw_symptom_text: str
    detected_language: str = "en"
    scoring_method: str = "llm"
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

# --- #3: POST /screening/extract ---
@router.post("/extract", response_model=ExtractResponse)
async def extract_symptoms(
    request: ExtractRequest,
    worker: ASHAWorker = Depends(get_current_worker),
):
    """Extract structured symptoms from raw patient text.

    Calls Gemini 2.0 Flash (primary) or Groq Llama 3.3 (fallback).
    """
    llm = LLMService()
    result = await llm.extract_symptoms(request.symptom_text, request.language)
    return ExtractResponse(**result)


# --- #4: POST /screening/score ---
@router.post("/score", response_model=ScoreResponse)
async def score_risk(
    request: ScoreRequest,
    worker: ASHAWorker = Depends(get_current_worker),
):
    """Score risk from extracted symptoms and demographics.

    Calls Gemini 2.0 Flash (primary) or Groq Llama 3.3 (fallback).
    If both LLMs fail, falls back to offline deterministic scorer.
    """
    llm = LLMService()
    result = await llm.score_risk(
        symptoms={"symptoms": request.symptoms},
        demographics=request.demographics,
    )
    return ScoreResponse(**result)


# --- #5: POST /screening/explain ---
@router.post("/explain", response_model=ExplainResponse)
async def explain_score(
    request: ExplainRequest,
    worker: ASHAWorker = Depends(get_current_worker),
):
    """Generate a plain-language explanation of the risk score.

    Returns explanation in the patient's preferred language (en/hi/te).
    """
    llm = LLMService()
    scoring_data = {
        "risk_score": request.risk_score,
        "risk_tier": request.risk_tier,
        "top_contributors": request.top_contributors,
        "recommendation_type": request.recommendation_type,
    }
    result = await llm.generate_explanation(scoring_data, request.language)
    return ExplainResponse(**result)


# --- #6: POST /screening/recommend ---
@router.post("/recommend", response_model=RecommendResponse)
async def generate_recommendation(
    request: RecommendRequest,
    worker: ASHAWorker = Depends(get_current_worker),
):
    """Generate actionable recommendation content for the patient."""
    llm = LLMService()
    result = await llm.generate_recommendation(
        recommendation_type=request.recommendation_type,
        top_symptoms=request.top_symptoms,
        risk_tier=request.risk_tier,
        patient_language=request.language,
    )
    return RecommendResponse(**result)


# --- #7: POST /screening/complete ---
@router.post("/complete", response_model=CompleteSessionResponse, status_code=201)
async def complete_session(
    request: CompleteSessionRequest,
    worker: ASHAWorker = Depends(get_current_worker),
    db: AsyncSession = Depends(get_db),
):
    """Save a fully completed screening session to PostgreSQL.

    Called after the app has collected extraction, scoring,
    explanation, and recommendation results.
    """
    session = ScreeningSession(
        patient_id=request.patient_id,
        asha_worker_id=worker.id,
        raw_symptom_text=request.symptom_text,
        detected_language=request.language,
        input_mode=request.input_mode,
        extracted_symptoms=request.extraction,
        risk_score=request.scoring.get("risk_score"),
        risk_tier=request.scoring.get("risk_tier"),
        red_flag_triggered=request.scoring.get("red_flag_triggered", False),
        red_flag_reason=request.scoring.get("red_flag_reason"),
        scoring_result=request.scoring,
        recommendation_type=request.scoring.get("recommendation_type"),
        recommendation_details=request.recommendation,
        explanation=request.explanation,
        scoring_method=request.scoring_method,
        llm_model_used=request.llm_model_used,
        llm_latency_ms=request.llm_latency_ms,
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)

    # Increment ASHA worker screening count
    worker.total_screenings += 1

    return CompleteSessionResponse(
        session_id=session.id,
        risk_score=session.risk_score or 0,
        risk_tier=session.risk_tier or "low",
        recommendation_type=session.recommendation_type or "self_care",
        created_at=session.created_at,
    )


# --- #8: GET /screening/sessions ---
@router.get("/sessions", response_model=list[SessionListItem])
async def list_sessions(
    worker: ASHAWorker = Depends(get_current_worker),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Get all screening sessions for the current ASHA worker.

    Returns most recent sessions first, with pagination.
    """
    result = await db.execute(
        select(ScreeningSession)
        .where(ScreeningSession.asha_worker_id == worker.id)
        .order_by(ScreeningSession.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    sessions = result.scalars().all()
    return [SessionListItem.model_validate(s) for s in sessions]
