"""
PDF Report Generator (Task M2-03)
==================================
Professional HealthBridge AI patient screening report using ReportLab.

Features:
  - Text-based logo header + branded layout
  - Large colored risk-score circle + tier badge
  - Extracted symptoms table with severity
  - LLM explanation bullets
  - Color-coded recommendation box
  - Bilingual Unicode: Hindi (Devanagari) & Telugu via Noto Sans
  - Returns PDF as bytes (BytesIO) for FastAPI StreamingResponse
  - Disclaimer footer with emergency numbers

Usage (in a router):
    from app.services.pdf_service import generate_report
    pdf_bytes = await generate_report(session, language="hi")
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf")
"""

import io
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.graphics.shapes import Drawing, Circle, String, Rect, Line
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ═══════════════════════════════════════════════════════════════════════════
# BRAND COLORS  (matching task spec)
# ═══════════════════════════════════════════════════════════════════════════

BRAND_PRIMARY   = HexColor("#1565C0")   # deep blue
BRAND_DARK      = HexColor("#0D47A1")   # header blue
BRAND_LIGHT     = HexColor("#E3F2FD")   # light blue bg
BRAND_TEXT      = HexColor("#212121")   # near-black text
BRAND_GRAY      = HexColor("#757575")   # muted text
BRAND_WHITE     = HexColor("#FFFFFF")

# Tier-specific colors (from spec)
TIER_COLORS = {
    "low":      HexColor("#27AE60"),   # green
    "moderate": HexColor("#F39C12"),   # orange
    "high":     HexColor("#E74C3C"),   # red
    "critical": HexColor("#C0392B"),   # dark red
}

TIER_BG_COLORS = {
    "low":      HexColor("#EAFAF1"),
    "moderate": HexColor("#FEF9E7"),
    "high":     HexColor("#FDEDEC"),
    "critical": HexColor("#F9EBEA"),
}

TIER_LABELS = {
    "low":      "LOW RISK",
    "moderate": "MODERATE RISK",
    "high":     "HIGH RISK",
    "critical": "CRITICAL",
}


# ═══════════════════════════════════════════════════════════════════════════
# FONT REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════

FONT_DIR = Path(__file__).parent.parent.parent / "fonts"
_fonts_registered = False


def _register_fonts():
    """Register Noto Sans fonts for Unicode (Hindi/Telugu) support.
    Falls back to Helvetica if font files are not found.
    """
    global _fonts_registered
    if _fonts_registered:
        return

    font_map = {
        "NotoSans":           "NotoSans-Regular.ttf",
        "NotoSansDevanagari": "NotoSansDevanagari-Regular.ttf",
        "NotoSansTelugu":     "NotoSansTelugu-Regular.ttf",
    }

    for font_name, filename in font_map.items():
        font_path = FONT_DIR / filename
        if font_path.exists():
            try:
                pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
            except Exception:
                pass  # Fall back to Helvetica

    _fonts_registered = True


def _get_font(language: str) -> str:
    """Return the best font name for the given language."""
    _register_fonts()
    if language == "hi":
        try:
            pdfmetrics.getFont("NotoSansDevanagari")
            return "NotoSansDevanagari"
        except KeyError:
            pass
    elif language == "te":
        try:
            pdfmetrics.getFont("NotoSansTelugu")
            return "NotoSansTelugu"
        except KeyError:
            pass
    # Try NotoSans for general Latin
    try:
        pdfmetrics.getFont("NotoSans")
        return "NotoSans"
    except KeyError:
        return "Helvetica"


# ═══════════════════════════════════════════════════════════════════════════
# RISK SCORE CIRCLE GRAPHIC
# ═══════════════════════════════════════════════════════════════════════════

def _draw_score_circle(score: int, tier: str, width: float = 80, height: float = 80) -> Drawing:
    """Draw a large colored circle with the risk score number inside."""
    d = Drawing(width, height)
    cx, cy = width / 2, height / 2
    radius = min(width, height) / 2 - 4

    color = TIER_COLORS.get(tier, BRAND_GRAY)

    # Outer circle
    circle = Circle(cx, cy, radius, fillColor=color, strokeColor=color, strokeWidth=2)
    d.add(circle)

    # Inner circle (lighter)
    inner = Circle(cx, cy, radius - 4, fillColor=white, strokeColor=color, strokeWidth=1.5)
    d.add(inner)

    # Score number
    score_str = str(score)
    font_size = 26 if score < 100 else 22
    text = String(cx, cy - font_size / 3, score_str,
                  fontSize=font_size, fontName="Helvetica-Bold",
                  fillColor=color, textAnchor="middle")
    d.add(text)

    # "/100" label below
    label = String(cx, cy - radius + 6, "/100",
                   fontSize=8, fontName="Helvetica",
                   fillColor=BRAND_GRAY, textAnchor="middle")
    d.add(label)

    return d


def _draw_tier_badge(tier: str, width: float = 120, height: float = 26) -> Drawing:
    """Draw a colored tier badge (pill shape)."""
    d = Drawing(width, height)
    color = TIER_COLORS.get(tier, BRAND_GRAY)
    label = TIER_LABELS.get(tier, tier.upper())

    # Rounded rectangle (approximated)
    r = Rect(2, 2, width - 4, height - 4, rx=10, ry=10,
             fillColor=color, strokeColor=color)
    d.add(r)

    text = String(width / 2, height / 2 - 4, label,
                  fontSize=11, fontName="Helvetica-Bold",
                  fillColor=white, textAnchor="middle")
    d.add(text)

    return d


# ═══════════════════════════════════════════════════════════════════════════
# MAIN PDF GENERATOR
# ═══════════════════════════════════════════════════════════════════════════

async def generate_report(session_data, language: str = "en") -> bytes:
    """Generate a professional HealthBridge AI screening report.

    Args:
        session_data: ScreeningSession ORM object or dict with session fields.
        language:     Patient language for bilingual content (en|hi|te).

    Returns:
        PDF file as bytes — ready for StreamingResponse.
    """
    _register_fonts()
    body_font = _get_font(language)

    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=12 * mm,
        bottomMargin=18 * mm,
        title="HealthBridge AI Screening Report",
        author="HealthBridge AI",
    )

    # ── Resolve fields from ORM object or dict ──
    if isinstance(session_data, dict):
        _g = session_data.get
    else:
        _g = lambda k, d=None: getattr(session_data, k, d)

    session_id      = str(_g("id", "N/A"))[:8]
    created_at      = _g("created_at", datetime.now(timezone.utc))
    risk_score      = _g("risk_score", 0) or 0
    risk_tier       = (_g("risk_tier", "low") or "low").lower()
    red_flag        = _g("red_flag_triggered", False)
    red_flag_reason = _g("red_flag_reason", None)
    raw_text        = _g("raw_symptom_text", "")
    rec_type        = _g("recommendation_type", "self_care") or "self_care"
    symptoms_json   = _g("extracted_symptoms", {}) or {}
    scoring_json    = _g("scoring_result", {}) or {}
    explanation_json = _g("explanation", {}) or {}
    recommendation_json = _g("recommendation_details", {}) or {}
    input_mode      = _g("input_mode", "text")
    det_lang        = _g("detected_language", language)

    tier_color = TIER_COLORS.get(risk_tier, BRAND_GRAY)
    tier_bg    = TIER_BG_COLORS.get(risk_tier, BRAND_LIGHT)

    # ── Styles ──
    styles = getSampleStyleSheet()

    s_title = ParagraphStyle("BrandTitle", parent=styles["Title"],
        fontSize=22, textColor=BRAND_DARK, fontName="Helvetica-Bold",
        spaceAfter=1 * mm, alignment=TA_LEFT)

    s_subtitle = ParagraphStyle("BrandSub", parent=styles["Normal"],
        fontSize=12, textColor=BRAND_PRIMARY, fontName="Helvetica",
        spaceAfter=4 * mm)

    s_section = ParagraphStyle("SectionHead", parent=styles["Heading2"],
        fontSize=13, textColor=BRAND_DARK, fontName="Helvetica-Bold",
        spaceBefore=6 * mm, spaceAfter=2 * mm,
        borderPadding=(0, 0, 2, 0))

    s_body = ParagraphStyle("Body", parent=styles["Normal"],
        fontSize=10, textColor=BRAND_TEXT, fontName=body_font,
        leading=14, spaceAfter=2 * mm)

    s_body_bold = ParagraphStyle("BodyBold", parent=s_body,
        fontName="Helvetica-Bold")

    s_small = ParagraphStyle("Small", parent=styles["Normal"],
        fontSize=8, textColor=BRAND_GRAY, fontName="Helvetica",
        leading=10)

    s_disclaimer = ParagraphStyle("Disclaimer", parent=s_small,
        alignment=TA_CENTER, textColor=HexColor("#999999"))

    s_redflag = ParagraphStyle("RedFlag", parent=s_body,
        textColor=TIER_COLORS["critical"], fontName="Helvetica-Bold",
        fontSize=11, backColor=HexColor("#F9EBEA"),
        borderPadding=(4, 8, 4, 8))

    elements = []

    # ══════════════════════════════════════════════════════════════════
    # HEADER
    # ══════════════════════════════════════════════════════════════════

    # Logo + title row
    logo_text = Paragraph(
        '<font color="#1565C0" size="24"><b>&#x2795; HealthBridge AI</b></font>',
        s_title,
    )
    elements.append(logo_text)
    elements.append(Paragraph("Patient Pre-Screening Report", s_subtitle))
    elements.append(HRFlowable(width="100%", thickness=2, color=BRAND_PRIMARY,
                               spaceAfter=4 * mm))

    # ══════════════════════════════════════════════════════════════════
    # PATIENT INFO BOX
    # ══════════════════════════════════════════════════════════════════

    elements.append(Paragraph("Patient Information", s_section))

    ts_str = created_at.strftime("%d %b %Y, %I:%M %p") if hasattr(created_at, "strftime") else str(created_at)

    info_data = [
        ["Session ID",  session_id + "...",   "Date & Time", ts_str],
        ["Language",     det_lang.upper(),     "Input Mode",  input_mode.title()],
    ]
    info_table = Table(info_data, colWidths=[30 * mm, 50 * mm, 30 * mm, 55 * mm])
    info_table.setStyle(TableStyle([
        ("FONTNAME",    (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",    (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",   (0, 0), (0, -1), BRAND_PRIMARY),
        ("TEXTCOLOR",   (2, 0), (2, -1), BRAND_PRIMARY),
        ("TEXTCOLOR",   (1, 0), (1, -1), BRAND_TEXT),
        ("TEXTCOLOR",   (3, 0), (3, -1), BRAND_TEXT),
        ("BACKGROUND",  (0, 0), (-1, -1), BRAND_LIGHT),
        ("BOX",         (0, 0), (-1, -1), 0.5, BRAND_PRIMARY),
        ("TOPPADDING",  (0, 0), (-1, -1), 3 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
    ]))
    elements.append(info_table)

    # ══════════════════════════════════════════════════════════════════
    # RISK SCORE SECTION
    # ══════════════════════════════════════════════════════════════════

    elements.append(Paragraph("Risk Assessment", s_section))

    score_circle = _draw_score_circle(risk_score, risk_tier)
    tier_badge = _draw_tier_badge(risk_tier)

    rec_label = rec_type.replace("_", " ").title()
    rec_paragraph = Paragraph(
        f'<font size="10"><b>Recommended Action:</b></font><br/>'
        f'<font size="11" color="{tier_color.hexval()}">'
        f'<b>{rec_label}</b></font>',
        s_body,
    )

    # Layout: circle | tier badge + recommendation
    score_row = Table(
        [[score_circle, tier_badge, rec_paragraph]],
        colWidths=[25 * mm, 40 * mm, 95 * mm],
        rowHeights=[25 * mm],
    )
    score_row.setStyle(TableStyle([
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
        ("BACKGROUND",  (0, 0), (-1, -1), tier_bg),
        ("BOX",         (0, 0), (-1, -1), 1, tier_color),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    elements.append(score_row)

    # Red flag alert
    if red_flag and red_flag_reason:
        elements.append(Spacer(1, 3 * mm))
        elements.append(Paragraph(
            f'\u26a0\ufe0f  RED FLAG: {red_flag_reason}', s_redflag
        ))

    # ══════════════════════════════════════════════════════════════════
    # TOP SYMPTOMS
    # ══════════════════════════════════════════════════════════════════

    elements.append(Paragraph("Reported Symptoms", s_section))
    elements.append(Paragraph(
        f'<i>"{raw_text}"</i>', s_small
    ))
    elements.append(Spacer(1, 2 * mm))

    symptom_list = symptoms_json.get("symptoms", [])
    if symptom_list:
        sym_header = [["#", "Symptom", "Body System", "Severity", "Confidence"]]
        sym_rows = []
        for i, s in enumerate(symptom_list[:10], 1):
            name = s.get("name", "unknown").replace("_", " ").title()
            system = s.get("body_system", "—")
            sev = s.get("severity_hint", "unknown")
            conf = f'{s.get("confidence", 0):.0%}'
            sym_rows.append([str(i), name, system, sev.title(), conf])

        sym_table = Table(sym_header + sym_rows,
                          colWidths=[8 * mm, 45 * mm, 35 * mm, 28 * mm, 22 * mm])
        sym_table.setStyle(TableStyle([
            ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, -1), 9),
            ("BACKGROUND",   (0, 0), (-1, 0), BRAND_PRIMARY),
            ("TEXTCOLOR",    (0, 0), (-1, 0), white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, BRAND_LIGHT]),
            ("BOX",          (0, 0), (-1, -1), 0.5, BRAND_GRAY),
            ("INNERGRID",    (0, 0), (-1, -1), 0.25, HexColor("#E0E0E0")),
            ("TOPPADDING",   (0, 0), (-1, -1), 2 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
            ("LEFTPADDING",  (0, 0), (-1, -1), 2 * mm),
            ("ALIGN",        (0, 0), (0, -1), "CENTER"),
            ("ALIGN",        (4, 0), (4, -1), "CENTER"),
        ]))
        elements.append(sym_table)
    else:
        elements.append(Paragraph("No structured symptoms extracted.", s_body))

    # ══════════════════════════════════════════════════════════════════
    # EXPLANATION
    # ══════════════════════════════════════════════════════════════════

    elements.append(Paragraph("What This Means", s_section))

    score_summary = explanation_json.get("score_summary", "")
    if score_summary:
        elements.append(Paragraph(f"<b>{score_summary}</b>", s_body))

    why_items = explanation_json.get("why_this_score", [])
    for i, reason in enumerate(why_items[:3], 1):
        elements.append(Paragraph(
            f'<font color="{BRAND_PRIMARY.hexval()}"><b>{i}.</b></font> {reason}',
            s_body,
        ))

    what_means = explanation_json.get("what_it_means", "")
    if what_means:
        elements.append(Paragraph(what_means, s_body))

    urgency = explanation_json.get("urgency_statement", "")
    if urgency:
        elements.append(Paragraph(
            f'<font color="{tier_color.hexval()}"><b>{urgency}</b></font>',
            s_body,
        ))

    # ══════════════════════════════════════════════════════════════════
    # RECOMMENDATION BOX
    # ══════════════════════════════════════════════════════════════════

    elements.append(Paragraph("Recommended Action", s_section))

    rec_items = []

    primary_action = recommendation_json.get("primary_action", "")
    if primary_action:
        rec_items.append(Paragraph(
            f'<font size="12" color="{tier_color.hexval()}"><b>{primary_action}</b></font>',
            s_body,
        ))

    steps = recommendation_json.get("steps", [])
    for i, step in enumerate(steps[:5], 1):
        rec_items.append(Paragraph(f"<b>Step {i}:</b> {step}", s_body))

    home_tips = recommendation_json.get("home_care_tips")
    if home_tips:
        rec_items.append(Spacer(1, 1 * mm))
        rec_items.append(Paragraph("<b>Home Care Tips:</b>", s_body))
        for tip in home_tips[:4]:
            rec_items.append(Paragraph(f"\u2022 {tip}", s_body))

    warning_signs = recommendation_json.get("warning_signs", [])
    if warning_signs:
        rec_items.append(Spacer(1, 1 * mm))
        rec_items.append(Paragraph(
            '<font color="#C0392B"><b>Warning Signs — Seek Immediate Help If:</b></font>',
            s_body,
        ))
        for ws in warning_signs[:3]:
            rec_items.append(Paragraph(
                f'<font color="#C0392B">\u26a0 {ws}</font>', s_body
            ))

    follow_up = recommendation_json.get("follow_up", "")
    if follow_up:
        rec_items.append(Spacer(1, 1 * mm))
        rec_items.append(Paragraph(f"<b>Follow-up:</b> {follow_up}", s_body))

    emergency_num = recommendation_json.get("emergency_number")
    teleconsult = recommendation_json.get("teleconsult_link")
    if emergency_num:
        rec_items.append(Paragraph(
            f'<font color="#C0392B" size="12"><b>Emergency: Call {emergency_num}</b></font>',
            s_body,
        ))
    if teleconsult:
        rec_items.append(Paragraph(
            f'<font color="{BRAND_PRIMARY.hexval()}">Teleconsult: '
            f'<u>{teleconsult}</u></font>',
            s_body,
        ))

    # Wrap in a colored box
    if rec_items:
        rec_inner = Table([[item] for item in rec_items], colWidths=[155 * mm])
        rec_inner.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, -1), tier_bg),
            ("BOX",         (0, 0), (-1, -1), 1.5, tier_color),
            ("TOPPADDING",  (0, 0), (-1, -1), 1.5 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5 * mm),
            ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
        ]))
        elements.append(rec_inner)

    # ══════════════════════════════════════════════════════════════════
    # FOOTER
    # ══════════════════════════════════════════════════════════════════

    elements.append(Spacer(1, 8 * mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=BRAND_GRAY))
    elements.append(Spacer(1, 2 * mm))

    elements.append(Paragraph(
        '<font color="#999999" size="8">'
        '<b>Disclaimer:</b> This report is for screening guidance only. '
        'It does NOT constitute a medical diagnosis. '
        'Please consult a qualified medical professional for proper evaluation and treatment. '
        'In case of emergency, call <b>108</b> immediately.'
        '</font>',
        s_disclaimer,
    ))
    elements.append(Spacer(1, 2 * mm))

    gen_time = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    elements.append(Paragraph(
        f'<font color="#BDBDBD" size="7">'
        f'HealthBridge AI  |  healthbridge.in  |  Generated: {gen_time}'
        f'</font>',
        s_disclaimer,
    ))

    # ── Build PDF ──
    doc.build(elements)
    pdf_bytes = buf.getvalue()
    buf.close()

    return pdf_bytes


# ═══════════════════════════════════════════════════════════════════════════
# FILE-BASED GENERATION (for backward compatibility)
# ═══════════════════════════════════════════════════════════════════════════

REPORTS_DIR = Path(__file__).parent.parent.parent / "reports"


class PDFService:
    """Wrapper class for router compatibility (saves to disk + returns path)."""

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir) if output_dir else REPORTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_screening_report(self, session) -> Path:
        """Generate PDF and save to disk. Returns file path."""
        import asyncio

        # Run the async generator synchronously
        loop = asyncio.new_event_loop()
        try:
            pdf_bytes = loop.run_until_complete(
                generate_report(session, language=getattr(session, "detected_language", "en"))
            )
        finally:
            loop.close()

        filename = f"report_{getattr(session, 'id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = self.output_dir / filename
        filepath.write_bytes(pdf_bytes)
        return filepath
