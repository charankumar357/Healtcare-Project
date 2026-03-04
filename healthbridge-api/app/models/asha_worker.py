"""ASHA Worker SQLAlchemy model."""

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ASHAWorker(Base):
    __tablename__ = "asha_workers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_hash: Mapped[str] = mapped_column(
        String(64), unique=True, index=True,
        comment="SHA-256 hash of phone number"
    )
    password_hash: Mapped[str] = mapped_column(
        String(128), nullable=False,
        comment="bcrypt hash of password"
    )
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    phc_name: Mapped[str | None] = mapped_column(
        String(200), nullable=True,
        comment="Primary Health Centre name"
    )
    preferred_language: Mapped[str] = mapped_column(
        String(5), default="en", comment="en|hi|te|ta|kn"
    )
    total_screenings: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    sessions = relationship("ScreeningSession", back_populates="asha_worker", lazy="selectin")

    def __repr__(self) -> str:
        return f"<ASHAWorker id={self.id} name={self.name} district={self.district}>"
