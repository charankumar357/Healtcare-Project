"""
Report router — PDF report generation.

#10  GET /report/{session_id}/pdf  —  Generate and return PDF report
"""

import io
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.session import ScreeningSession
from app.models.asha_worker import ASHAWorker
from app.routers.auth import get_current_worker
from app.services.pdf_service import generate_report

router = APIRouter(prefix="/report", tags=["Reports"])


@router.get("/{session_id}/pdf")
async def get_pdf_report(
    session_id: UUID,
    language: str = Query("en", pattern="^(en|hi|te|ta|kn)$"),
    worker: ASHAWorker = Depends(get_current_worker),
    db: AsyncSession = Depends(get_db),
):
    """Generate and return a PDF screening report.

    Returns the PDF as a streaming download.
    Query param `language` controls bilingual content (en|hi|te|ta|kn).
    """
    result = await db.execute(
        select(ScreeningSession).where(ScreeningSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    pdf_bytes = await generate_report(session, language=language)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="healthbridge_report_{session_id}.pdf"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )
