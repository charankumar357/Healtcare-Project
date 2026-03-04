"""Auth-related Pydantic schemas."""

from uuid import UUID
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login request for ASHA workers."""
    phone: str = Field(..., min_length=10, max_length=15, description="Phone number")
    password: str = Field(..., min_length=6, max_length=128)


class LoginResponse(BaseModel):
    """JWT login response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Token expiry in seconds")
    worker: "WorkerProfile"


class WorkerProfile(BaseModel):
    """ASHA worker public profile."""
    id: UUID
    name: str
    district: str
    state: str
    phc_name: str | None = None
    preferred_language: str
    total_screenings: int

    model_config = {"from_attributes": True}


class RegisterRequest(BaseModel):
    """ASHA worker registration."""
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=6, max_length=128)
    district: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    phc_name: str | None = None
    preferred_language: str = Field("en", pattern="^(en|hi|te|ta|kn)$")


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str  # worker UUID
    exp: int
