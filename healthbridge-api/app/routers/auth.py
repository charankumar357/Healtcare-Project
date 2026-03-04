"""
Auth router — ASHA worker registration and login (JWT-based).
OTP endpoints are excluded per project requirements.
"""

import hashlib
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.asha_worker import ASHAWorker
from app.schemas.auth import (
    LoginRequest, LoginResponse, RegisterRequest, WorkerProfile,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_phone(phone: str) -> str:
    """SHA-256 hash of phone number for privacy."""
    return hashlib.sha256(phone.encode()).hexdigest()


def create_access_token(worker_id: UUID) -> tuple[str, int]:
    """Create a JWT access token. Returns (token, expires_in_seconds)."""
    expires_in = settings.jwt_expiry_minutes * 60
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiry_minutes)
    payload = {"sub": str(worker_id), "exp": expire}
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, expires_in


async def get_current_worker(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> ASHAWorker:
    """FastAPI dependency: extract and verify current ASHA worker from JWT.

    Use as: worker: ASHAWorker = Depends(get_current_worker)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        worker_id = payload.get("sub")
        if worker_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(
        select(ASHAWorker).where(ASHAWorker.id == UUID(worker_id))
    )
    worker = result.scalar_one_or_none()
    if worker is None or not worker.is_active:
        raise credentials_exception
    return worker


# ─── Endpoints ───────────────────────────────────────────────────────


@router.post("/register", response_model=WorkerProfile, status_code=201)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new ASHA worker account."""
    phone_h = hash_phone(request.phone)

    existing = await db.execute(
        select(ASHAWorker).where(ASHAWorker.phone_hash == phone_h)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Phone number already registered")

    worker = ASHAWorker(
        name=request.name,
        phone_hash=phone_h,
        password_hash=pwd_context.hash(request.password),
        district=request.district,
        state=request.state,
        phc_name=request.phc_name,
        preferred_language=request.preferred_language,
    )
    db.add(worker)
    await db.flush()
    await db.refresh(worker)
    return worker


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login with phone + password and receive a JWT access token."""
    phone_h = hash_phone(request.phone)

    result = await db.execute(
        select(ASHAWorker).where(ASHAWorker.phone_hash == phone_h)
    )
    worker = result.scalar_one_or_none()

    if not worker or not pwd_context.verify(request.password, worker.password_hash):
        raise HTTPException(status_code=401, detail="Invalid phone or password")

    if not worker.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    worker.last_login_at = datetime.now(timezone.utc)
    token, expires_in = create_access_token(worker.id)

    return LoginResponse(
        access_token=token,
        expires_in=expires_in,
        worker=WorkerProfile.model_validate(worker),
    )


@router.get("/me", response_model=WorkerProfile)
async def get_me(worker: ASHAWorker = Depends(get_current_worker)):
    """Get current authenticated ASHA worker profile."""
    return WorkerProfile.model_validate(worker)
