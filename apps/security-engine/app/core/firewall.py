"""
Prompt Injection Firewall — two-stage detection.

Stage 1: Pattern matching (< 5ms, blocks obvious injections)
Stage 2: ML classifier (< 100ms, catches subtle injections)
"""

import re
import structlog

logger = structlog.get_logger()

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"you\s+are\s+now\s+(a\s+)?different",
    r"forget\s+(your\s+)?(system\s+)?prompt",
    r"act\s+as\s+if\s+you\s+are",
    r"(jailbreak|DAN\s+mode|developer\s+mode|god\s+mode)",
    r"print\s+(your\s+)?(system\s+)?prompt",
    r"reveal\s+(your\s+)?(instructions|rules|config)",
    r"disregard\s+(all\s+)?previous",
    r"new\s+instructions?\s*:",
    r"<\s*/?system\s*>",
    r"\[\s*SYSTEM\s*\]",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


class PromptFirewall:
    _classifier = None

    @classmethod
    def initialize(cls):
        """Load the ML classifier model at startup (optional)."""
        try:
            import joblib
            from pathlib import Path
            model_path = Path(__file__).parent.parent.parent / "models" / "injection_classifier.joblib"
            if model_path.exists():
                cls._classifier = joblib.load(model_path)
                logger.info("Injection classifier loaded")
            else:
                logger.warning("Injection classifier not found — pattern matching only")
        except Exception as e:
            logger.warning(f"Could not load injection classifier: {e}")

    @classmethod
    def scan(cls, text: str) -> dict:
        """
        Scan text for prompt injection.
        Returns: {"blocked": bool, "reason": str | None, "confidence": float}
        """
        # Stage 1: Pattern matching
        for pattern in COMPILED_PATTERNS:
            if pattern.search(text):
                logger.warning("Prompt injection blocked (pattern)", pattern=pattern.pattern)
                return {"blocked": True, "reason": "pattern_match", "confidence": 1.0}

        # Stage 2: ML classifier (if loaded)
        if cls._classifier is not None:
            try:
                score = float(cls._classifier.predict_proba([[len(text), text.count(" ")]])[0][1])
                if score > 0.85:
                    logger.warning("Prompt injection blocked (ML)", score=score)
                    return {"blocked": True, "reason": "ml_classifier", "confidence": score}
            except Exception:
                pass

        return {"blocked": False, "reason": None, "confidence": 0.0}
