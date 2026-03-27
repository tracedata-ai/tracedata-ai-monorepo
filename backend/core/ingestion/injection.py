"""
Injection Scanner — OWASP LLM01:2025 mitigation.

Scans all string fields in a TelemetryPacket for:
  - Known prompt injection phrases
  - System prompt extraction attempts
  - SQL injection patterns
  - HTML/script injection
  - Control characters (null bytes, non-printable)
  - Oversized fields (prompt stuffing defence — OWASP LLM10)

Applied at the ingestion boundary before any data reaches agents or LLMs.

Location: backend/core/ingestion/injection.py
"""

import logging
import os
import re
from typing import Any

logger = logging.getLogger(__name__)

# ── PATTERN LIBRARY ──────────────────────────────────────────────────────────
# Compiled once at import time for performance.
# Patterns grouped by attack category for maintainability.

# Prompt injection — LLM instruction override attempts
_PROMPT_INJECTION: list[re.Pattern] = [
    re.compile(r"ignore\s+(previous|all|prior)\s+instructions?", re.I),
    re.compile(r"forget\s+(everything|all|your)\s+instructions?", re.I),
    re.compile(r"disregard\s+(your|all|safety|previous|the\s+above)", re.I),
    re.compile(r"you\s+are\s+now\s+a", re.I),
    re.compile(r"act\s+as\s+(if\s+you\s+are|a\s+different)", re.I),
    re.compile(r"new\s+instructions?\s*:", re.I),
    re.compile(r"override\s+(safety|previous|all|your)", re.I),
    re.compile(r"pretend\s+(you\s+are|to\s+be)", re.I),
    re.compile(r"roleplay\s+as", re.I),
    re.compile(r"from\s+now\s+on\s+you\s+(are|will)", re.I),
]

# System prompt extraction attempts
_SYSTEM_EXTRACTION: list[re.Pattern] = [
    re.compile(r"\[?\s*(SYSTEM|INST|SYS)\s*\]?\s*:", re.I),
    re.compile(r"repeat\s+(your\s+)?(system\s+)?instructions?", re.I),
    re.compile(r"(show|print|output|reveal)\s+(your\s+)?(system\s+)?prompt", re.I),
    re.compile(r"what\s+(are|were)\s+your\s+instructions?", re.I),
    re.compile(r"print\s+everything\s+above", re.I),
]

# SQL injection — covers common patterns
_SQL_INJECTION: list[re.Pattern] = [
    re.compile(r"--\s*$", re.M),  # SQL comment
    re.compile(r";\s*(DROP|DELETE|TRUNCATE|ALTER)\s+", re.I),
    re.compile(r"\bUNION\s+(ALL\s+)?SELECT\b", re.I),
    re.compile(r"'\s*(OR|AND)\s+'?\d+'?\s*=\s*'?\d+", re.I),  # ' OR '1'='1
    re.compile(r"xp_cmdshell", re.I),
    re.compile(r"EXEC\s*\(", re.I),
    re.compile(r"CAST\s*\(.*AS\s+", re.I),
]

# HTML / script injection
_HTML_INJECTION: list[re.Pattern] = [
    re.compile(r"<\s*(script|iframe|img|svg|object|embed|link)", re.I),
    re.compile(r"javascript\s*:", re.I),
    re.compile(r"on(load|click|error|mouseover)\s*=", re.I),
    re.compile(r"data\s*:\s*text/html", re.I),
]

# Control characters (null byte injection, CRLF injection)
_CONTROL_CHARS: re.Pattern = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

ALL_PATTERNS: list[tuple[str, re.Pattern]] = (
    [("prompt_injection", p) for p in _PROMPT_INJECTION]
    + [("system_extraction", p) for p in _SYSTEM_EXTRACTION]
    + [("sql_injection", p) for p in _SQL_INJECTION]
    + [("html_injection", p) for p in _HTML_INJECTION]
    + [("control_chars", _CONTROL_CHARS)]
)

MAX_STRING_LENGTH: int = int(os.getenv("MAX_STRING_LENGTH", "2000"))
SCAN_ENABLED: bool = os.getenv("INJECTION_SCAN_ENABLED", "true").lower() == "true"


class InjectionScanner:
    """
    Recursively scans all string fields in a dict/list structure.
    Stateless — safe to reuse across requests.
    """

    def scan(self, data: Any) -> tuple[bool, str | None]:
        """
        Entry point. Recursively walks the full payload.

        Returns:
            (True, None)       — clean, safe to proceed
            (False, reason)    — injection detected, route to DLQ
        """
        if not SCAN_ENABLED:
            return True, None

        return self._scan_value(data)

    # ── PRIVATE ───────────────────────────────────────────────────────────────

    def _scan_value(self, value: Any) -> tuple[bool, str | None]:

        if isinstance(value, str):
            return self._scan_string(value)

        elif isinstance(value, dict):
            for k, v in value.items():
                ok, reason = self._scan_value(v)
                if not ok:
                    return False, f"field '{k}': {reason}"
            return True, None

        elif isinstance(value, list):
            for i, item in enumerate(value):
                ok, reason = self._scan_value(item)
                if not ok:
                    return False, f"index {i}: {reason}"
            return True, None

        # int, float, bool, None — safe
        return True, None

    def _scan_string(self, value: str) -> tuple[bool, str | None]:

        # Length check — prompt stuffing defence (OWASP LLM10)
        if len(value) > MAX_STRING_LENGTH:
            return (
                False,
                f"field length {len(value)} exceeds max {MAX_STRING_LENGTH}",
            )

        # Pattern matching
        for category, pattern in ALL_PATTERNS:
            if pattern.search(value):
                # Log only first 100 chars — never log the full injection payload
                preview = value[:100].replace("\n", "\\n")
                logger.warning(
                    {
                        "action": "injection_pattern_matched",
                        "category": category,
                        "pattern": pattern.pattern[:80],
                        "preview": preview,
                    }
                )
                return False, f"{category} pattern detected"

        return True, None
