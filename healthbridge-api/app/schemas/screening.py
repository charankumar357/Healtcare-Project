"""Pydantic v2 schemas for screening endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ─── Symptom Input ───

class SymptomInput(BaseModel):
    """Single symptom as extracted or reported."""
    name: str = Field(..., description="English symptom key, e.g. 'fever'")
    severity: str = Field("unknown", pattern="^(mild|moderate|severe|unknown)$")
    duration: str = Field(
        "unknown",
        pattern="^(acute|acute_less_24h|subacute|subacute_1_7days|chronic|chronic_more_7days|unknown)$",
    )
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    original_text: Optional[str] = Field(None, description="Original phrase from patient")
    body_system: Optional[str] = None


class ScreeningRequest(BaseModel):
    """Request body for POST /screening/analyze."""
    symptom_text: str = Field(
        ..., min_length=3, max_length=2000,
        description="Raw symptom text from patient (any supported language)",
    )
    patient_id: Optional[UUID] = None
    language: str = Field("auto", description="Language hint: auto|en|hi|te|ta|kn")
    input_mode: str = Field("text", pattern="^(text|voice)$")
    demographics: Optional["PatientDemographics"] = None


class PatientDemographics(BaseModel):
    """Demographics for risk score modifiers."""
    age: int = Field(..., ge=0, le=120)
    gender: str = Field("unknown", pattern="^(male|female|other|unknown)$")
    comorbidities: list[str] = Field(default_factory=list)
    is_pregnant: bool = False


# ─── Extraction Response ───

class ExtractionResult(BaseModel):
    """Response from symptom extraction."""
    symptoms: list[SymptomInput]
    detected_language: str
    input_quality: str = Field("clear", pattern="^(clear|noisy|ambiguous)$")
    clarification_needed: list[str] = Field(default_factory=list)


# ─── Scoring Response ───

class TopContributor(BaseModel):
    """A top-contributing symptom to the risk score."""
    symptom: str
    weight_contribution: float
    reason: str


class ScoringResult(BaseModel):
    """Risk scoring result — matches LLM output schema."""
    risk_score: int = Field(..., ge=0, le=100)
    risk_tier: str = Field(..., pattern="^(low|moderate|high|critical)$")
    top_contributors: list[TopContributor]
    red_flag_triggered: bool
    red_flag_reason: Optional[str] = None
    recommendation_type: str = Field(
        ..., pattern="^(self_care|teleconsultation|hospital_visit|emergency)$"
    )
    confidence: float = Field(..., ge=0.0, le=1.0)


# ─── Explanation ───

class ExplanationResult(BaseModel):
    """Plain-language explanation for the patient."""
    explanation_language: str
    score_summary: str
    why_this_score: list[str]
    what_it_means: str
    what_to_do_now: str
    urgency_statement: str


# ─── Recommendation ───

class RecommendationResult(BaseModel):
    """Actionable recommendation for the patient."""
    primary_action: str
    steps: list[str]
    home_care_tips: Optional[list[str]] = None
    warning_signs: list[str]
    follow_up: str
    emergency_number: Optional[str] = None
    teleconsult_link: Optional[str] = None
    nearby_facility_search: bool = False


# ─── Full Screening Response ───

class ScreeningResponse(BaseModel):
    """Complete response for POST /screening/analyze."""
    session_id: UUID
    extraction: ExtractionResult
    scoring: ScoringResult
    explanation: ExplanationResult
    recommendation: RecommendationResult
    scoring_method: str = Field("llm", pattern="^(llm|offline)$")
    processing_time_ms: int


# ─── Session Summary (for list views) ───

class SessionSummary(BaseModel):
    """Lightweight session info for list endpoints."""
    id: UUID
    risk_score: Optional[int] = None
    risk_tier: Optional[str] = None
    recommendation_type: Optional[str] = None
    created_at: datetime
    scoring_method: str = "llm"

    model_config = {"from_attributes": True}


# ─── Offline Sync ───

class OfflineSession(BaseModel):
    """A single session from offline batch sync."""
    device_id: str
    offline_created_at: datetime
    symptom_text: str
    language: str = "auto"
    input_mode: str = "text"
    patient_age: int
    patient_gender: str = "unknown"
    comorbidities: list[str] = Field(default_factory=list)
    is_pregnant: bool = False
    # Offline scorer results (computed on device)
    offline_risk_score: Optional[int] = None
    offline_risk_tier: Optional[str] = None


class OfflineSyncRequest(BaseModel):
    """Batch sync request from ASHA device."""
    worker_id: UUID
    device_id: str
    sessions: list[OfflineSession]


class OfflineSyncResponse(BaseModel):
    """Response for batch sync."""
    synced_count: int
    failed_count: int
    session_ids: list[UUID]
    errors: list[str] = Field(default_factory=list)
