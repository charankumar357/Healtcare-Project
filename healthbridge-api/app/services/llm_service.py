"""
LLM Orchestration Service (Task M2-02)
=======================================
Async LLM orchestration with dual-provider fallback and Redis caching.

PRIMARY  : Google Gemini 2.0 Flash  — forced JSON output via response_mime_type
FALLBACK : Groq + Llama 3.3 70B    — triggered on rate-limit / quota / error

All 4 system prompts from systemprompts.txt are embedded here.
Results are cached in Redis (TTL=3600) keyed by SHA-256(input).
"""

import hashlib
import json
import logging
import re
import time
from typing import Optional

from app.config import settings

logger = logging.getLogger("healthbridge.llm")


# ═══════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPTS  (from systemprompts.txt — identical to LLM API behaviour)
# ═══════════════════════════════════════════════════════════════════════════

SYMPTOM_EXTRACTION_PROMPT = """You are a medical symptom extraction engine for a rural health pre-screening application in India.
Your ONLY job is to extract structured symptom data from patient-reported free text or voice transcripts.

INPUT: Raw text (may be in Hindi, Telugu, Tamil, Kannada, or English). May contain noise, grammar errors,
or informal phrasing like 'sir pet mein dard ho raha hai do din se'.

OUTPUT: Return ONLY a valid JSON object — no preamble, no explanation, no markdown backticks.

JSON schema:
{
  "symptoms": [
    {
      "name": "string (English symptom name — underscore_case)",
      "original_text": "string (exact phrase from input)",
      "body_system": "respiratory|gastrointestinal|cardiovascular|neurological|systemic|musculoskeletal|dermatological|reproductive|ophthalmological|ent",
      "severity_hint": "mild|moderate|severe|unknown",
      "duration_hint": "acute_less_24h|subacute_1_7days|chronic_more_7days|unknown",
      "confidence": 0.0-1.0
    }
  ],
  "detected_language": "en|hi|te|ta|kn|mr|other",
  "input_quality": "clear|noisy|ambiguous",
  "clarification_needed": ["list of unclear symptoms needing follow-up questions"]
}

RULES:
1. Map all symptom names to English regardless of input language
2. If a symptom name is ambiguous, set confidence < 0.7 and add to clarification_needed
3. Never infer symptoms not explicitly stated — only extract what the patient mentions
4. A single input may contain 1-15 symptoms"""


RISK_SCORING_PROMPT = """You are a clinical risk scoring engine for a rural health pre-screening system in India.
You analyze structured symptom data and produce a risk score and classification.

INPUT: A JSON object with symptoms array (from symptom extraction), patient demographics,
and known comorbidities.

CRITICAL SAFETY RULES — these OVERRIDE your score calculation:
If ANY of the following are present, immediately set risk_score >= 85 and tier = 'critical':
- chest_pain AND (shortness_of_breath OR dyspnea)
- sudden_paralysis OR sudden_facial_drooping OR sudden_slurred_speech
- loss_of_consciousness OR unresponsive
- active_seizure
- severe_difficulty_breathing in a patient under age 5
- suspected_poisoning OR drug_overdose
- uncontrolled_bleeding OR hemorrhage
- cyanosis AND (shortness_of_breath OR rapid_breathing)
- chest_pain AND left_arm_pain

SCORING LOGIC:
- Base score = sum of symptom weights (see knowledge graph: each symptom has base_weight 1-20)
- Multiply by: duration modifier (acute=1.0, subacute=1.2, chronic=1.5)
- Multiply by: comorbidity modifier (none=1.0, diabetes/hypertension=1.3, both=1.6, pregnancy=1.4)
- Multiply by: symptom combination bonus (2+ same system=1.2, cross-system=1.4)
- Clamp to 0-100

OUTPUT: Return ONLY valid JSON — no preamble, no markdown:
{
  "risk_score": 0-100,
  "risk_tier": "low|moderate|high|critical",
  "top_contributors": [
    {"symptom": "string", "weight_contribution": number, "reason": "one sentence"}
  ],
  "red_flag_triggered": true|false,
  "red_flag_reason": "string or null",
  "recommendation_type": "self_care|teleconsultation|hospital_visit|emergency",
  "confidence": 0.0-1.0
}

TIER MAPPING: low=0-29 | moderate=30-59 | high=60-84 | critical=85-100
ALWAYS err toward HIGHER risk when uncertain. It is safer to over-classify."""


EXPLAINABILITY_PROMPT = """You are a health explanation engine for rural patients in India, many of whom have low health literacy.

INPUT: A JSON with risk_score, risk_tier, top_contributors, recommendation_type, and patient language.

Your task: Generate a plain-language explanation of the risk score in the patient's language.

OUTPUT: Return ONLY valid JSON:
{
  "explanation_language": "en|hi|te|ta|kn",
  "score_summary": "1-2 sentences: what the score means in simple terms",
  "why_this_score": [
    "Plain language sentence for top contributor 1",
    "Plain language sentence for top contributor 2",
    "Plain language sentence for top contributor 3"
  ],
  "what_it_means": "1 sentence about what this risk level means for their health",
  "what_to_do_now": "Specific, actionable 1-2 sentence instruction",
  "urgency_statement": "A single bold sentence stating time urgency"
}

LANGUAGE RULES:
- If language = hi: Write all text fields in simple Hindi (Devanagari script)
- If language = te: Write all text fields in simple Telugu
- If language = en or unknown: Write in simple English (Grade 5 reading level)
- NEVER use medical jargon. Replace 'dyspnea' with 'difficulty breathing' etc.
- Use short sentences. Maximum 20 words per sentence.
- Be direct, not alarming. Calm, clear, helpful tone."""


RECOMMENDATION_PROMPT = """You are a health recommendation engine for rural India. Generate specific, actionable advice.

INPUT: recommendation_type (self_care|teleconsultation|hospital_visit|emergency),
top symptoms, risk_tier, patient_age, patient_language.

OUTPUT: Return ONLY valid JSON:
{
  "primary_action": "Single most important thing to do RIGHT NOW",
  "steps": ["Step 1", "Step 2", "Step 3"],
  "home_care_tips": ["tip1", "tip2"] or null if not self_care,
  "warning_signs": ["If you see X, escalate immediately"],
  "follow_up": "When and how to follow up",
  "emergency_number": "108" or null,
  "teleconsult_link": "https://esanjeevani.mohfw.gov.in" or null,
  "nearby_facility_search": true|false
}

For emergency tier: steps[0] must ALWAYS be 'Call 108 immediately'
For hospital_visit: always include nearby_facility_search: true
Keep all text in {patient_language}
Maximum 15 words per step. Mobile screen readability is critical."""


# ═══════════════════════════════════════════════════════════════════════════
# REDIS CACHE HELPER
# ═══════════════════════════════════════════════════════════════════════════

_redis_client = None
_redis_available = False

CACHE_TTL = 3600  # 1 hour


async def _get_redis():
    """Lazy-init Redis connection."""
    global _redis_client, _redis_available
    if _redis_client is None:
        try:
            import redis.asyncio as aioredis
            _redis_client = aioredis.from_url(
                settings.redis_url, decode_responses=True
            )
            await _redis_client.ping()
            _redis_available = True
            logger.info("Redis cache connected")
        except Exception as e:
            _redis_available = False
            logger.warning(f"Redis unavailable — caching disabled: {e}")
    return _redis_client if _redis_available else None


def _cache_key(system_prompt: str, user_message: str) -> str:
    """SHA-256 hash of (system_prompt + user_message)."""
    raw = f"{system_prompt}||{user_message}"
    return f"llm_cache:{hashlib.sha256(raw.encode()).hexdigest()}"


async def _cache_get(key: str) -> Optional[dict]:
    """Get cached LLM result."""
    redis = await _get_redis()
    if redis:
        try:
            data = await redis.get(key)
            if data:
                logger.info(f"Cache HIT: {key[:30]}...")
                return json.loads(data)
        except Exception:
            pass
    return None


async def _cache_set(key: str, value: dict):
    """Cache LLM result with TTL."""
    redis = await _get_redis()
    if redis:
        try:
            await redis.set(key, json.dumps(value, default=str), ex=CACHE_TTL)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════════
# LLM PROVIDER CALLS
# ═══════════════════════════════════════════════════════════════════════════

async def _gemini_generate(system_prompt: str, user_message: str) -> str:
    """Call Google Gemini 2.0 Flash with forced JSON output.

    Raises on rate-limit or quota errors so fallback can trigger.
    """
    import google.generativeai as genai

    genai.configure(api_key=settings.gemini_api_key)

    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        system_instruction=system_prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.1,
            response_mime_type="application/json",
        ),
    )

    response = await model.generate_content_async(
        user_message,
        request_options={"timeout": settings.llm_timeout},
    )

    return response.text


async def _groq_generate(system_prompt: str, user_message: str) -> str:
    """Call Groq Llama 3.3 70B as fallback with JSON mode."""
    from groq import AsyncGroq

    client = AsyncGroq(api_key=settings.groq_api_key)

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ],
        temperature=0.1,
        max_tokens=2048,
        response_format={"type": "json_object"},
        timeout=settings.llm_timeout,
    )

    return response.choices[0].message.content


def _clean_json_response(raw: str) -> str:
    """Strip markdown backticks / code fences if the model wrapped JSON."""
    cleaned = raw.strip()
    # Remove ```json ... ``` wrapping
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


# ═══════════════════════════════════════════════════════════════════════════
# UNIFIED call_llm()  — Gemini → Groq fallback
# ═══════════════════════════════════════════════════════════════════════════

async def call_llm(system_prompt: str, user_message: str) -> dict:
    """
    Unified async LLM call with:
      1. Redis cache check
      2. Gemini 2.0 Flash  (primary)
      3. Groq Llama 3.3    (fallback on rate-limit / error)
      4. JSON cleanup       (strip markdown fences)
      5. Structured logging (model, tokens, latency)

    Returns: parsed JSON dict from the LLM.
    Raises: ValueError if both providers fail.
    """
    # ── 1. Cache check ──
    key = _cache_key(system_prompt, user_message)
    cached = await _cache_get(key)
    if cached is not None:
        return cached

    raw_text: Optional[str] = None
    provider: str = "none"
    start = time.perf_counter()

    # ── 2. Try Gemini (primary) ──
    if settings.gemini_api_key:
        try:
            raw_text = await _gemini_generate(system_prompt, user_message)
            provider = "gemini-2.0-flash"
        except Exception as gemini_err:
            err_str = str(gemini_err)
            is_rate_limit = any(k in err_str for k in ("429", "RATE_LIMIT", "RESOURCE_EXHAUSTED", "quota"))
            logger.warning(
                f"Gemini failed ({'rate-limit' if is_rate_limit else 'error'}): {err_str[:120]}"
            )
            # Fall through to Groq

    # ── 3. Fallback to Groq ──
    if raw_text is None and settings.groq_api_key:
        try:
            raw_text = await _groq_generate(system_prompt, user_message)
            provider = "llama-3.3-70b-versatile"
            logger.info("Fallback to Groq succeeded")
        except Exception as groq_err:
            logger.error(f"Groq fallback also failed: {groq_err}")

    # ── 4. Both failed ──
    if raw_text is None:
        raise ValueError(
            "Both LLM providers failed. Check API keys and quotas. "
            "Set GEMINI_API_KEY and/or GROQ_API_KEY in .env"
        )

    latency_ms = int((time.perf_counter() - start) * 1000)

    # ── 5. Parse JSON (with cleanup) ──
    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        cleaned = _clean_json_response(raw_text)
        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError as je:
            logger.error(f"JSON parse failed after cleanup. Raw: {raw_text[:300]}")
            raise ValueError(f"LLM returned invalid JSON: {je}") from je

    # ── 6. Log structured metrics ──
    logger.info(json.dumps({
        "event": "llm_call",
        "provider": provider,
        "latency_ms": latency_ms,
        "input_chars": len(user_message),
        "output_chars": len(raw_text),
        "cache": "miss",
    }))

    # ── 7. Cache result ──
    await _cache_set(key, result)

    return result


# Store last-call metadata for the screening router
class _CallMeta:
    """Tracks metadata from the most recent call_llm invocation."""
    provider: str = "none"
    latency_ms: int = 0
    tokens: Optional[int] = None
    method: str = "llm"   # "llm" or "offline"

_meta = _CallMeta()


async def _tracked_call(system_prompt: str, user_message: str) -> dict:
    """Wrapper around call_llm that updates _meta."""
    start = time.perf_counter()
    result = await call_llm(system_prompt, user_message)
    _meta.latency_ms = int((time.perf_counter() - start) * 1000)
    _meta.method = "llm"
    return result


# ═══════════════════════════════════════════════════════════════════════════
# SERVICE METHODS — used by the screening router
# ═══════════════════════════════════════════════════════════════════════════

class LLMService:
    """High-level service consumed by routers.

    Each method calls call_llm() with the correct system prompt,
    then falls back to offline logic if both LLMs are unavailable.
    """

    def __init__(self):
        self.last_method: str = "llm"
        self.last_model: Optional[str] = None
        self.last_latency_ms: Optional[int] = None
        self.last_tokens: Optional[int] = None

    # ── 1. Symptom Extraction ──────────────────────────────────────────

    async def extract_symptoms(self, symptom_text: str, language: str = "auto") -> dict:
        """Extract structured symptoms from raw patient text."""
        user_msg = f"Patient input (language hint: {language}):\n{symptom_text}"
        try:
            result = await call_llm(SYMPTOM_EXTRACTION_PROMPT, user_msg)
            self._update_meta("llm")
            return result
        except ValueError:
            self._update_meta("offline")
            return self._offline_extraction(symptom_text, language)

    # ── 2. Risk Scoring ────────────────────────────────────────────────

    async def score_risk(self, symptoms: dict, demographics: Optional[dict] = None) -> dict:
        """Score risk from extracted symptoms and demographics."""
        user_msg = json.dumps({
            "symptoms": symptoms.get("symptoms", []),
            "demographics": demographics or {},
        })
        try:
            result = await call_llm(RISK_SCORING_PROMPT, user_msg)
            self._update_meta("llm")
            return result
        except ValueError:
            self._update_meta("offline")
            return self._offline_score(symptoms, demographics)

    # ── 3. Explanation ─────────────────────────────────────────────────

    async def generate_explanation(self, scoring_result: dict, language: str = "en") -> dict:
        """Generate a plain-language explanation for the patient."""
        user_msg = json.dumps({**scoring_result, "patient_language": language})
        try:
            result = await call_llm(EXPLAINABILITY_PROMPT, user_msg)
            self._update_meta("llm")
            return result
        except ValueError:
            self._update_meta("offline")
            return self._offline_explanation(scoring_result, language)

    # ── 4. Recommendation ─────────────────────────────────────────────

    async def generate_recommendation(
        self,
        recommendation_type: str,
        top_symptoms: list,
        risk_tier: str,
        patient_language: str = "en",
    ) -> dict:
        """Generate actionable next-step recommendation."""
        user_msg = json.dumps({
            "recommendation_type": recommendation_type,
            "top_symptoms": top_symptoms,
            "risk_tier": risk_tier,
            "patient_language": patient_language,
        })
        try:
            result = await call_llm(RECOMMENDATION_PROMPT, user_msg)
            self._update_meta("llm")
            return result
        except ValueError:
            self._update_meta("offline")
            return self._offline_recommendation(recommendation_type)

    # ── Meta helpers ───────────────────────────────────────────────────

    def _update_meta(self, method: str):
        self.last_method = method
        self.last_model = _meta.provider if method == "llm" else "offline_scorer"
        self.last_latency_ms = _meta.latency_ms
        self.last_tokens = _meta.tokens

    # ═══════════════════════════════════════════════════════════════════
    # OFFLINE FALLBACKS  (when both Gemini + Groq are down)
    # ═══════════════════════════════════════════════════════════════════

    def _offline_extraction(self, symptom_text: str, language: str) -> dict:
        """Basic symptom extraction without LLM."""
        return {
            "symptoms": [{
                "name": symptom_text.lower().replace(" ", "_")[:60],
                "original_text": symptom_text,
                "body_system": "unknown",
                "severity_hint": "unknown",
                "duration_hint": "unknown",
                "confidence": 0.5,
            }],
            "detected_language": language if language != "auto" else "en",
            "input_quality": "ambiguous",
            "clarification_needed": [],
        }

    def _offline_score(self, symptoms: dict, demographics: Optional[dict]) -> dict:
        """Fall back to the deterministic offline scorer from M3-02."""
        import sys
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        # The offline scorer lives one level above healthbridge-api/
        parent_dir = os.path.dirname(project_root)
        sys.path.insert(0, parent_dir)
        try:
            from offline_scorer import create_scorer
            scorer = create_scorer()
            symptom_list = []
            for s in symptoms.get("symptoms", []):
                symptom_list.append({
                    "name": s.get("name", ""),
                    "severity": s.get("severity_hint", "unknown"),
                    "duration": s.get("duration_hint", "unknown"),
                    "confidence": s.get("confidence", 0.9),
                })
            return scorer.calculate_score(symptom_list, demographics)
        except Exception as e:
            logger.error(f"Offline scorer also failed: {e}")
            return {
                "risk_score": 50,
                "risk_tier": "moderate",
                "top_contributors": [],
                "red_flag_triggered": False,
                "red_flag_reason": None,
                "recommendation_type": "teleconsultation",
                "confidence": 0.3,
            }

    def _offline_explanation(self, scoring: dict, language: str) -> dict:
        tier = scoring.get("risk_tier", "moderate")
        return {
            "explanation_language": language,
            "score_summary": f"Your health check shows {tier} concern level.",
            "why_this_score": [
                c.get("reason", "") for c in scoring.get("top_contributors", [])[:3]
            ],
            "what_it_means": f"This means your symptoms need {tier} level attention.",
            "what_to_do_now": "Please consult a healthcare provider for proper evaluation.",
            "urgency_statement": "Do not delay seeking care if symptoms worsen.",
        }

    def _offline_recommendation(self, rec_type: str) -> dict:
        recs = {
            "emergency": {
                "primary_action": "Call 108 immediately",
                "steps": ["Call 108 immediately", "Do not move the patient", "Keep patient warm"],
                "home_care_tips": None,
                "warning_signs": ["If breathing stops, start CPR"],
                "follow_up": "Follow up at hospital within 24 hours",
                "emergency_number": "108",
                "teleconsult_link": None,
                "nearby_facility_search": True,
            },
            "hospital_visit": {
                "primary_action": "Visit nearest hospital today",
                "steps": ["Go to nearest PHC or hospital", "Carry any previous reports", "Describe all symptoms to doctor"],
                "home_care_tips": None,
                "warning_signs": ["If symptoms worsen, call 108"],
                "follow_up": "Follow up in 3 days if not better",
                "emergency_number": None,
                "teleconsult_link": None,
                "nearby_facility_search": True,
            },
            "teleconsultation": {
                "primary_action": "Book a teleconsultation",
                "steps": ["Visit esanjeevani.mohfw.gov.in", "Register with Aadhaar/phone", "Consult online doctor"],
                "home_care_tips": ["Rest well", "Drink plenty of fluids"],
                "warning_signs": ["If fever goes above 103F, visit hospital"],
                "follow_up": "Follow up in 5-7 days",
                "emergency_number": None,
                "teleconsult_link": "https://esanjeevani.mohfw.gov.in",
                "nearby_facility_search": False,
            },
            "self_care": {
                "primary_action": "Rest and monitor symptoms at home",
                "steps": ["Take rest", "Stay hydrated", "Monitor symptoms for 2-3 days"],
                "home_care_tips": ["Eat light meals", "Get enough sleep", "Wash hands frequently"],
                "warning_signs": ["If symptoms worsen or new symptoms appear, consult doctor"],
                "follow_up": "See a doctor if not better in 3 days",
                "emergency_number": None,
                "teleconsult_link": None,
                "nearby_facility_search": False,
            },
        }
        return recs.get(rec_type, recs["teleconsultation"])
