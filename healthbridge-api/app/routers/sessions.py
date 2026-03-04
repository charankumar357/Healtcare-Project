"""
Sessions router — offline sync endpoint.

#9  POST /sessions/sync  —  Batch sync offline sessions from ASHA device
"""

from uuid import UUID
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.session import ScreeningSession
from app.models.patient import Patient
from app.models.asha_worker import ASHAWorker
from app.routers.auth import get_current_worker
from app.services.llm_service import LLMService

router = APIRouter(prefix="/sessions", tags=["Sessions"])


class OfflineSession(BaseModel):
    """A single session from offline batch sync."""
    device_id: str
    offline_created_at: datetime
    symptom_text: str
    language: str = "auto"
    input_mode: str = Field("text", pattern="^(text|voice)$")
    patient_age: int = Field(..., ge=0, le=120)
    patient_gender: str = Field("unknown", pattern="^(male|female|other|unknown)$")
    comorbidities: list[str] = Field(default_factory=list)
    is_pregnant: bool = False
    offline_risk_score: Optional[int] = None
    offline_risk_tier: Optional[str] = None


class SyncRequest(BaseModel):
    """POST /sessions/sync"""
    device_id: str
    sessions: list[OfflineSession]


class SyncResponse(BaseModel):
    synced_count: int
    failed_count: int
    session_ids: list[UUID]
    errors: list[str] = Field(default_factory=list)


@router.post("/sync", response_model=SyncResponse)
async def sync_offline_sessions(
    request: SyncRequest,
    worker: ASHAWorker = Depends(get_current_worker),
    db: AsyncSession = Depends(get_db),
):
    """Batch sync offline sessions from ASHA device.

    Re-processes each session through the LLM pipeline
    to verify offline scores and store canonical results.
    """
    synced_ids: list[UUID] = []
    errors: list[str] = []
    llm = LLMService()

    for i, offline in enumerate(request.sessions):
        try:
            # Create patient record
            patient = Patient(
                phone_hash=f"offline-{request.device_id}-{i}",
                age=offline.patient_age,
                gender=offline.patient_gender,
                comorbidities=str(offline.comorbidities) if offline.comorbidities else None,
                is_pregnant=offline.is_pregnant,
            )
            db.add(patient)
            await db.flush()

            # Re-score via LLM
            extraction = await llm.extract_symptoms(offline.symptom_text, offline.language)
            scoring = await llm.score_risk(
                symptoms=extraction,
                demographics={
                    "age": offline.patient_age,
                    "comorbidities": offline.comorbidities,
                    "pregnancy": offline.is_pregnant,
                },
            )

            session = ScreeningSession(
                patient_id=patient.id,
                asha_worker_id=worker.id,
                raw_symptom_text=offline.symptom_text,
                detected_language=extraction.get("detected_language", offline.language),
                input_mode=offline.input_mode,
                extracted_symptoms=extraction,
                risk_score=scoring.get("risk_score"),
                risk_tier=scoring.get("risk_tier"),
                red_flag_triggered=scoring.get("red_flag_triggered", False),
                red_flag_reason=scoring.get("red_flag_reason"),
                scoring_result=scoring,
                recommendation_type=scoring.get("recommendation_type"),
                scoring_method="llm",
                is_synced=True,
                device_id=request.device_id,
                offline_created_at=offline.offline_created_at,
            )
            db.add(session)
            await db.flush()
            synced_ids.append(session.id)

            # Count towards ASHA stats
            worker.total_screenings += 1

        except Exception as e:
            errors.append(f"Session {i}: {str(e)}")

    return SyncResponse(
        synced_count=len(synced_ids),
        failed_count=len(errors),
        session_ids=synced_ids,
        errors=errors,
    )
