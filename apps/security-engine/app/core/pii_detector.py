"""
PII Detection & Masking using Microsoft Presidio + regex patterns.
"""

import re
import structlog

logger = structlog.get_logger()

# Regex patterns for common PII types
PII_PATTERNS = {
    "email": (
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        lambda m: f"{m[0]}***@{m.split('@')[1]}" if "@" in m else "***@***",
    ),
    "phone": (
        r"\b(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
        lambda m: "***-***-" + m[-4:],
    ),
    "ssn": (
        r"\b\d{3}-\d{2}-\d{4}\b",
        lambda m: "***-**-" + m[-4:],
    ),
    "credit_card": (
        r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        lambda m: "****-****-****-" + m.replace(" ", "").replace("-", "")[-4:],
    ),
    "ip_address": (
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        lambda m: "***.***.***.***",
    ),
}


class PIIDetector:
    @staticmethod
    def detect(text: str) -> list[dict]:
        """Find all PII entities in the text."""
        findings = []
        for pii_type, (pattern, _) in PII_PATTERNS.items():
            for match in re.finditer(pattern, text):
                findings.append({
                    "type": pii_type,
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                })
        return sorted(findings, key=lambda x: x["start"])

    @staticmethod
    def mask(text: str) -> str:
        """Replace all detected PII with masked versions."""
        for pii_type, (pattern, masker) in PII_PATTERNS.items():
            def replace_match(m, fn=masker):
                try:
                    return fn(m.group())
                except Exception:
                    return "[REDACTED]"
            text = re.sub(pattern, replace_match, text)
        return text

    @staticmethod
    def contains_pii(text: str) -> bool:
        """Quick check — returns True if any PII is detected."""
        for pii_type, (pattern, _) in PII_PATTERNS.items():
            if re.search(pattern, text):
                return True
        return False
