"""
Audio router — voice-to-text via Groq Whisper API.

#12  POST /audio/transcribe  —  Receive audio file -> call Groq Whisper -> return transcript
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from app.models.asha_worker import ASHAWorker
from app.routers.auth import get_current_worker
from app.services.whisper_service import WhisperService

router = APIRouter(prefix="/audio", tags=["Audio"])


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    worker: ASHAWorker = Depends(get_current_worker),
):
    """Transcribe audio file to text using Groq Whisper API.

    Supports: mp3, wav, m4a, ogg, webm
    Max file size: 25MB
    """
    allowed_types = {"audio/mpeg", "audio/wav", "audio/mp4", "audio/ogg", "audio/webm",
                     "audio/x-wav", "audio/x-m4a", "audio/webm"}
    if audio.content_type and audio.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format: {audio.content_type}. "
                   f"Supported: mp3, wav, m4a, ogg, webm",
        )

    content = await audio.read()
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Audio file too large (max 25MB)")

    whisper = WhisperService()
    result = await whisper.transcribe(
        audio_bytes=content,
        filename=audio.filename or "audio.wav",
    )

    return result
