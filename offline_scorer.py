"""
Offline Deterministic Risk Scoring Engine (Task M3-02)
======================================================
Pure Python scoring engine using the symptom knowledge graph.
Runs on-device without internet — mirrors LLM scoring prompt logic exactly.

Designed for easy manual porting to JavaScript for React Native offline use.

Usage:
    scorer = OfflineRiskScorer("symptom_knowledge_graph.json")
    result = scorer.calculate_score(
        symptoms=[
            {"name": "fever", "severity": "moderate", "duration": "subacute"},
            {"name": "cough", "severity": "severe", "duration": "chronic"}
        ],
        demographics={"age": 45, "comorbidities": ["diabetes"]}
    )
"""

import json
import os
from typing import Optional


# ---------------------------------------------------------------------------
# Constants — keep in sync with RISK_SCORING_SYSTEM_PROMPT
# ---------------------------------------------------------------------------

TIER_THRESHOLDS = [
    (85, "critical"),
    (60, "high"),
    (30, "moderate"),
    (0,  "low"),
]

RECOMMENDATION_MAP = {
    "critical":  "emergency",
    "high":      "hospital_visit",
    "moderate":  "teleconsultation",
    "low":       "self_care",
}

DURATION_MODIFIERS = {
    "acute":           1.0,
    "acute_less_24h":  1.0,
    "subacute":        1.2,
    "subacute_1_7days": 1.2,
    "chronic":         1.5,
    "chronic_more_7days": 1.5,
    "unknown":         1.0,
}

COMORBIDITY_MODIFIERS = {
    frozenset():                          1.0,
    frozenset(["diabetes"]):              1.3,
    frozenset(["hypertension"]):          1.3,
    frozenset(["diabetes", "hypertension"]): 1.6,
    frozenset(["pregnancy"]):             1.4,
}

# Hard-coded critical overrides from the system prompt.
# These OVERRIDE any calculated score when matched.
CRITICAL_OVERRIDES = [
    {
        "condition": lambda syms, demo: (
            "chest_pain" in syms and
            ("shortness_of_breath" in syms or "dyspnea" in syms)
        ),
        "reason": "Chest pain with breathing difficulty — possible acute coronary syndrome or PE",
    },
    {
        "condition": lambda syms, demo: "sudden_paralysis" in syms,
        "reason": "Sudden paralysis — possible stroke, activate FAST protocol",
    },
    {
        "condition": lambda syms, demo: "facial_drooping" in syms,
        "reason": "Sudden facial drooping — possible stroke",
    },
    {
        "condition": lambda syms, demo: "slurred_speech" in syms,
        "reason": "Sudden slurred speech — possible stroke",
    },
    {
        "condition": lambda syms, demo: (
            "loss_of_consciousness" in syms or "unresponsive" in syms
        ),
        "reason": "Loss of consciousness — immediate evaluation needed",
    },
    {
        "condition": lambda syms, demo: "seizure" in syms,
        "reason": "Active seizure — emergency intervention required",
    },
    {
        "condition": lambda syms, demo: (
            "shortness_of_breath" in syms and
            demo.get("age", 99) < 5 and
            any(s_detail.get("severity") == "severe"
                for s_detail in demo.get("_symptom_details", [])
                if s_detail.get("name") == "shortness_of_breath")
        ),
        "reason": "Severe breathing difficulty in child under 5 — life-threatening",
    },
    {
        "condition": lambda syms, demo: (
            "suspected_poisoning" in syms or "drug_overdose" in syms
        ),
        "reason": "Suspected poisoning or overdose — call 108 immediately",
    },
    {
        "condition": lambda syms, demo: (
            "uncontrolled_bleeding" in syms or "hemorrhage" in syms
        ),
        "reason": "Uncontrolled bleeding — emergency intervention required",
    },
    {
        "condition": lambda syms, demo: (
            "cyanosis" in syms and
            ("shortness_of_breath" in syms or "rapid_breathing" in syms)
        ),
        "reason": "Cyanosis with breathing difficulty — severe respiratory failure",
    },
    {
        "condition": lambda syms, demo: (
            "chest_pain" in syms and "left_arm_pain" in syms
        ),
        "reason": "Chest pain radiating to left arm — possible myocardial infarction",
    },
]


# ---------------------------------------------------------------------------
# Main Scorer Class
# ---------------------------------------------------------------------------

class OfflineRiskScorer:
    """Deterministic risk scorer using the symptom knowledge graph."""

    def __init__(self, knowledge_graph_path: str):
        """Load the symptom knowledge graph JSON.

        Args:
            knowledge_graph_path: Absolute or relative path to
                symptom_knowledge_graph.json
        """
        with open(knowledge_graph_path, "r", encoding="utf-8") as f:
            self._kg = json.load(f)

        self._symptoms = self._kg.get("symptoms", {})
        self._red_flag_combos = self._kg.get("red_flag_combinations", [])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate_score(
        self,
        symptoms: list[dict],
        demographics: Optional[dict] = None,
    ) -> dict:
        """Calculate a deterministic risk score.

        Args:
            symptoms: List of dicts, each with keys:
                - name (str):     English symptom key, e.g. "fever"
                - severity (str): "mild" | "moderate" | "severe" | "unknown"
                - duration (str): "acute" | "subacute" | "chronic" | "unknown"
                                  (also accepts extraction aliases like
                                   "acute_less_24h", "subacute_1_7days", etc.)
                - confidence (float, optional): 0.0-1.0

            demographics: Optional dict with keys:
                - age (int)
                - comorbidities (list[str]): e.g. ["diabetes", "hypertension"]
                - pregnancy (bool)

        Returns:
            dict matching the LLM RISK_SCORING output JSON schema:
            {
                "risk_score": int 0-100,
                "risk_tier": str,
                "top_contributors": [...],
                "red_flag_triggered": bool,
                "red_flag_reason": str | None,
                "recommendation_type": str,
                "confidence": float
            }
        """
        demographics = demographics or {}
        symptom_names = [s["name"] for s in symptoms]

        # ---- Step 1: Critical override check (system prompt rules) ----
        override_triggered, override_reason = self._check_critical_overrides(
            symptom_names, demographics, symptoms
        )
        if override_triggered:
            return self._build_result(
                score=90,
                red_flag=True,
                red_flag_reason=override_reason,
                symptoms=symptoms,
                demographics=demographics,
            )

        # ---- Step 1b: Knowledge-graph red-flag combination check ----
        rf_triggered, rf_reason, rf_override = self.check_red_flags(symptom_names)
        if rf_triggered:
            return self._build_result(
                score=rf_override,
                red_flag=True,
                red_flag_reason=rf_reason,
                symptoms=symptoms,
                demographics=demographics,
            )

        # ---- Step 2: Per-symptom weighted scoring ----
        weighted_scores = []
        for sym in symptoms:
            name = sym["name"]
            severity = sym.get("severity", "unknown")
            duration = sym.get("duration", "unknown")
            confidence = sym.get("confidence", 1.0)

            kg_entry = self._symptoms.get(name)
            if kg_entry is None:
                # Unknown symptom — assign a default low weight
                weighted_scores.append({
                    "name": name,
                    "base": 3,
                    "severity_mult": 1.0,
                    "duration_mult": 1.0,
                    "weighted": 3.0,
                    "body_system": "unknown",
                })
                continue

            base = kg_entry["base_weight"]
            sev_mult = kg_entry["severity_multipliers"].get(severity, 1.0)
            dur_mult = DURATION_MODIFIERS.get(duration, 1.0)
            weighted = base * sev_mult * dur_mult * confidence

            weighted_scores.append({
                "name": name,
                "base": base,
                "severity_mult": sev_mult,
                "duration_mult": dur_mult,
                "weighted": weighted,
                "body_system": kg_entry["body_system"],
            })

        raw_score = sum(ws["weighted"] for ws in weighted_scores)

        # ---- Step 3: Comorbidity modifier ----
        comorbidity_mult = self._get_comorbidity_modifier(demographics)
        raw_score *= comorbidity_mult

        # ---- Step 4: Cross-system / same-system bonus ----
        system_bonus = self._get_system_bonus(weighted_scores)
        raw_score *= system_bonus

        # ---- Step 5: Clamp 0-100 ----
        score = int(min(100, max(0, round(raw_score))))

        # ---- Step 6 & 7: Build result ----
        return self._build_result(
            score=score,
            red_flag=False,
            red_flag_reason=None,
            symptoms=symptoms,
            demographics=demographics,
            weighted_scores=weighted_scores,
        )

    def check_red_flags(
        self, symptom_names: list[str]
    ) -> tuple[bool, Optional[str], int]:
        """Check knowledge-graph red_flag_combinations.

        Args:
            symptom_names: List of English symptom keys.

        Returns:
            (triggered: bool, reason: str|None, override_score: int)
        """
        symptom_set = set(symptom_names)
        best_match = None

        for combo in self._red_flag_combos:
            combo_syms = set(combo["symptoms"])
            if combo_syms.issubset(symptom_set):
                if best_match is None or combo["override_score"] > best_match["override_score"]:
                    best_match = combo

        if best_match:
            return True, best_match["reason"], best_match["override_score"]

        return False, None, 0

    def get_top_contributors(
        self,
        weighted_scores: list[dict],
        top_n: int = 3,
    ) -> list[dict]:
        """Return top N symptoms by weight contribution.

        Args:
            weighted_scores: The per-symptom scoring breakdown.
            top_n: Number of top contributors to return.

        Returns:
            List of dicts with symptom, weight_contribution, reason.
        """
        sorted_scores = sorted(
            weighted_scores, key=lambda x: x["weighted"], reverse=True
        )

        contributors = []
        for ws in sorted_scores[:top_n]:
            reason = self._explain_contributor(ws)
            contributors.append({
                "symptom": ws["name"],
                "weight_contribution": round(ws["weighted"], 1),
                "reason": reason,
            })

        return contributors

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _check_critical_overrides(
        self,
        symptom_names: list[str],
        demographics: dict,
        symptom_details: list[dict],
    ) -> tuple[bool, Optional[str]]:
        """Check hard-coded critical override rules from system prompt."""
        syms_set = set(symptom_names)
        # Attach symptom details so lambda can inspect severity
        demo_with_details = {**demographics, "_symptom_details": symptom_details}

        for rule in CRITICAL_OVERRIDES:
            if rule["condition"](syms_set, demo_with_details):
                return True, rule["reason"]

        return False, None

    def _get_comorbidity_modifier(self, demographics: dict) -> float:
        """Compute comorbidity modifier from demographics."""
        comorbidities = set(demographics.get("comorbidities", []))
        if demographics.get("pregnancy"):
            comorbidities.add("pregnancy")

        # Try exact match first
        key = frozenset(comorbidities)
        if key in COMORBIDITY_MODIFIERS:
            return COMORBIDITY_MODIFIERS[key]

        # Fallback: pick highest applicable modifier
        modifier = 1.0
        if "pregnancy" in comorbidities:
            modifier = max(modifier, 1.4)
        if "diabetes" in comorbidities and "hypertension" in comorbidities:
            modifier = max(modifier, 1.6)
        elif "diabetes" in comorbidities or "hypertension" in comorbidities:
            modifier = max(modifier, 1.3)

        return modifier

    def _get_system_bonus(self, weighted_scores: list[dict]) -> float:
        """Compute same-system / cross-system multiplier.

        Rules from system prompt:
            2+ symptoms in same system  → 1.2
            symptoms across 2+ systems  → 1.4
        """
        systems = [ws["body_system"] for ws in weighted_scores]
        unique_systems = set(systems)

        if len(unique_systems) >= 2:
            return 1.4
        # Check if 2+ symptoms in same system
        for sys in unique_systems:
            if systems.count(sys) >= 2:
                return 1.2

        return 1.0

    def _score_to_tier(self, score: int) -> str:
        """Map numeric score to risk tier."""
        for threshold, tier in TIER_THRESHOLDS:
            if score >= threshold:
                return tier
        return "low"

    def _build_result(
        self,
        score: int,
        red_flag: bool,
        red_flag_reason: Optional[str],
        symptoms: list[dict],
        demographics: dict,
        weighted_scores: Optional[list[dict]] = None,
    ) -> dict:
        """Build the final result dict matching LLM output schema."""
        tier = self._score_to_tier(score)

        if weighted_scores:
            top_contributors = self.get_top_contributors(weighted_scores)
        else:
            # Red-flag override — use symptom names directly
            top_contributors = [
                {
                    "symptom": s["name"],
                    "weight_contribution": self._symptoms.get(
                        s["name"], {}
                    ).get("base_weight", 10),
                    "reason": f"{s['name'].replace('_', ' ').title()} is a critical symptom",
                }
                for s in symptoms[:3]
            ]

        # Confidence: high for deterministic engine, slightly lower if
        # unknown symptoms present
        known_count = sum(
            1 for s in symptoms if s["name"] in self._symptoms
        )
        confidence = round(
            0.85 + 0.15 * (known_count / max(len(symptoms), 1)), 2
        )

        return {
            "risk_score": score,
            "risk_tier": tier,
            "top_contributors": top_contributors,
            "red_flag_triggered": red_flag,
            "red_flag_reason": red_flag_reason,
            "recommendation_type": RECOMMENDATION_MAP[tier],
            "confidence": confidence,
        }

    def _explain_contributor(self, ws: dict) -> str:
        """Generate a simple English explanation for a symptom contribution."""
        name_readable = ws["name"].replace("_", " ").title()
        base = ws["base"]
        body = ws["body_system"]

        if base >= 15:
            severity_desc = "a high-severity"
        elif base >= 10:
            severity_desc = "a moderate-to-high severity"
        elif base >= 6:
            severity_desc = "a moderate"
        else:
            severity_desc = "a low-severity"

        explanation = f"{name_readable} is {severity_desc} {body} symptom"

        if ws["severity_mult"] > 1.0:
            explanation += " with increased severity"
        if ws["duration_mult"] > 1.0:
            explanation += " persisting beyond acute phase"

        return explanation


# ---------------------------------------------------------------------------
# Convenience: module-level factory
# ---------------------------------------------------------------------------

def create_scorer(
    knowledge_graph_path: Optional[str] = None,
) -> OfflineRiskScorer:
    """Create an OfflineRiskScorer with default knowledge graph path.

    Args:
        knowledge_graph_path: Path to JSON file. Defaults to
            symptom_knowledge_graph.json in the same directory.

    Returns:
        OfflineRiskScorer instance ready to use.
    """
    if knowledge_graph_path is None:
        knowledge_graph_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "symptom_knowledge_graph.json",
        )
    return OfflineRiskScorer(knowledge_graph_path)


# ---------------------------------------------------------------------------
# CLI demo / self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    scorer = create_scorer()

    # --- Test 1: Red-flag critical override ---
    print("=" * 60)
    print("TEST 1: Critical red-flag override (chest_pain + SOB)")
    print("=" * 60)
    result = scorer.calculate_score(
        symptoms=[
            {"name": "chest_pain", "severity": "severe", "duration": "acute"},
            {"name": "shortness_of_breath", "severity": "severe", "duration": "acute"},
        ],
        demographics={"age": 55, "comorbidities": ["hypertension"]},
    )
    print(json.dumps(result, indent=2))
    assert result["risk_tier"] == "critical", "Should be critical!"
    assert result["red_flag_triggered"] is True

    # --- Test 2: Moderate case ---
    print("\n" + "=" * 60)
    print("TEST 2: Moderate case (fever + cough, subacute)")
    print("=" * 60)
    result = scorer.calculate_score(
        symptoms=[
            {"name": "fever", "severity": "moderate", "duration": "subacute"},
            {"name": "cough", "severity": "moderate", "duration": "subacute"},
        ],
        demographics={"age": 30, "comorbidities": []},
    )
    print(json.dumps(result, indent=2))
    print(f"Tier: {result['risk_tier']}")

    # --- Test 3: Low severity ---
    print("\n" + "=" * 60)
    print("TEST 3: Low severity (runny nose, mild, acute)")
    print("=" * 60)
    result = scorer.calculate_score(
        symptoms=[
            {"name": "runny_nose", "severity": "mild", "duration": "acute"},
        ],
        demographics={"age": 25, "comorbidities": []},
    )
    print(json.dumps(result, indent=2))
    assert result["risk_tier"] == "low", "Should be low!"

    # --- Test 4: KG red-flag combo ---
    print("\n" + "=" * 60)
    print("TEST 4: KG red-flag combo (blood_in_sputum + weight_loss + night_sweats)")
    print("=" * 60)
    result = scorer.calculate_score(
        symptoms=[
            {"name": "blood_in_sputum", "severity": "moderate", "duration": "chronic"},
            {"name": "weight_loss", "severity": "moderate", "duration": "chronic"},
            {"name": "night_sweats", "severity": "moderate", "duration": "chronic"},
        ],
        demographics={"age": 40, "comorbidities": []},
    )
    print(json.dumps(result, indent=2))
    assert result["red_flag_triggered"] is True, "TB triad should trigger red flag!"

    # --- Test 5: Comorbidity escalation ---
    print("\n" + "=" * 60)
    print("TEST 5: Comorbidity escalation (diabetes + hypertension)")
    print("=" * 60)
    result = scorer.calculate_score(
        symptoms=[
            {"name": "headache", "severity": "severe", "duration": "subacute"},
            {"name": "dizziness", "severity": "moderate", "duration": "subacute"},
            {"name": "vision_changes", "severity": "moderate", "duration": "acute"},
        ],
        demographics={"age": 60, "comorbidities": ["diabetes", "hypertension"]},
    )
    print(json.dumps(result, indent=2))

    # --- Test 6: Stroke symptoms ---
    print("\n" + "=" * 60)
    print("TEST 6: Stroke override (sudden_paralysis + slurred_speech)")
    print("=" * 60)
    result = scorer.calculate_score(
        symptoms=[
            {"name": "sudden_paralysis", "severity": "severe", "duration": "acute"},
            {"name": "slurred_speech", "severity": "severe", "duration": "acute"},
        ],
        demographics={"age": 70, "comorbidities": ["hypertension"]},
    )
    print(json.dumps(result, indent=2))
    assert result["risk_tier"] == "critical"
    assert result["red_flag_triggered"] is True

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
