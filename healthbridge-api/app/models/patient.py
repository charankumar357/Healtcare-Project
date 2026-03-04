"""Patient SQLAlchemy model."""

import uuid
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Boolean, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    phone_hash: Mapped[str] = mapped_column(
        String(64), unique=True, index=True,
        comment="SHA-256 hash of phone number — we never store raw phone"
    )
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="male|female|other"
    )
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pincode: Mapped[str | None] = mapped_column(String(6), nullable=True)
    preferred_language: Mapped[str] = mapped_column(
        String(5), default="en", comment="en|hi|te|ta|kn"
    )
    comorbidities: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="JSON array string: ['diabetes','hypertension']"
    )
    is_pregnant: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    sessions = relationship("ScreeningSession", back_populates="patient", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Patient id={self.id} age={self.age} lang={self.preferred_language}>"
