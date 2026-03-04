"""Whisper Service — Groq Whisper API for voice-to-text transcription."""

import logging
import time
import json
from typing import Optional

from app.config import settings

logger = logging.getLogger("healthbridge.whisper")


class WhisperService:
    """Voice-to-text transcription using Groq's Whisper API."""

    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: Optional[str] = None,
    ) -> dict:
        """Transcribe audio bytes using Groq Whisper.

        Args:
            audio_bytes: Raw audio file bytes
            filename: Original filename (for MIME detection)
            language: Optional language hint (en, hi, te, ta)

        Returns:
            {
                "text": "transcribed text",
                "language": "detected language code",
                "duration_seconds": float,
                "latency_ms": int
            }
        """
        if not settings.groq_api_key:
            logger.warning("Groq API key not set — returning empty transcription")
            return {
                "text": "",
                "language": "unknown",
                "duration_seconds": 0,
                "latency_ms": 0,
                "error": "Groq API key not configured",
            }

        try:
            from groq import AsyncGroq
            import tempfile
            import os

            client = AsyncGroq(api_key=settings.groq_api_key)

            # Write to temp file (Groq SDK needs a file path)
            with tempfile.NamedTemporaryFile(
                suffix=os.path.splitext(filename)[1] or ".wav",
                delete=False,
            ) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            start = time.perf_counter()

            with open(tmp_path, "rb") as audio_file:
                transcription = await client.audio.transcriptions.create(
                    file=(filename, audio_file),
                    model="whisper-large-v3",
                    language=language,
                    response_format="verbose_json",
                    timeout=settings.llm_timeout,
                )

            latency_ms = int((time.perf_counter() - start) * 1000)

            # Cleanup temp file
            os.unlink(tmp_path)

            result = {
                "text": transcription.text,
                "language": getattr(transcription, "language", language or "unknown"),
                "duration_seconds": getattr(transcription, "duration", 0),
                "latency_ms": latency_ms,
            }

            logger.info(json.dumps({
                "event": "whisper_call",
                "model": "whisper-large-v3",
                "latency_ms": latency_ms,
                "text_length": len(result["text"]),
                "language": result["language"],
            }))

            return result

        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return {
                "text": "",
                "language": "unknown",
                "duration_seconds": 0,
                "latency_ms": 0,
                "error": str(e),
            }
