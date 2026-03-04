"""ScreeningSession SQLAlchemy model."""

import uuid
from datetime import datetime

from sqlalchemy import (
    String, Integer, Float, DateTime, Boolean, Text,
    ForeignKey, func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ScreeningSession(Base):
    __tablename__ = "screening_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True
    )
    asha_worker_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asha_workers.id"), nullable=True
    )

    # ─── Input ───
    raw_symptom_text: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Original symptom text (may be Hindi/Telugu/English)"
    )
    detected_language: Mapped[str] = mapped_column(
        String(5), default="en", comment="Language detected during extraction"
    )
    input_mode: Mapped[str] = mapped_column(
        String(10), default="text", comment="text|voice"
    )

    # ─── Extraction Result ───
    extracted_symptoms: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="JSON from symptom extraction LLM call"
    )

    # ─── Scoring Result ───
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_tier: Mapped[str | None] = mapped_column(
        String(10), nullable=True, comment="low|moderate|high|critical"
    )
    red_flag_triggered: Mapped[bool] = mapped_column(Boolean, default=False)
    red_flag_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    scoring_result: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="Full scoring JSON from LLM or offline scorer"
    )

    # ─── Recommendation ───
    recommendation_type: Mapped[str | None] = mapped_column(
        String(20), nullable=True,
        comment="self_care|teleconsultation|hospital_visit|emergency"
    )
    recommendation_details: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True
    )

    # ─── Explanation ───
    explanation: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="Plain-language explanation for the patient"
    )

    # ─── Metadata ───
    scoring_method: Mapped[str] = mapped_column(
        String(10), default="llm", comment="llm|offline"
    )
    llm_model_used: Mapped[str | None] = mapped_column(String(50), nullable=True)
    llm_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    llm_tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ─── PDF Report ───
    pdf_report_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ─── Offline Sync ───
    is_synced: Mapped[bool] = mapped_column(
        Boolean, default=True,
        comment="False if created offline and not yet synced"
    )
    device_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    offline_created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="Original creation time on device (if offline)"
    )

    # ─── Timestamps ───
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # ─── Relationships ───
    patient = relationship("Patient", back_populates="sessions")
    asha_worker = relationship("ASHAWorker", back_populates="sessions")

    def __repr__(self) -> str:
        return f"<ScreeningSession id={self.id} tier={self.risk_tier} score={self.risk_score}>"
