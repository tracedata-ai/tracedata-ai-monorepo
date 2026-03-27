import re


class InjectionScanner:
    """
    OWASP LLM01 / API8 Alignment.
    Scans untrusted telemetry payloads for malicious injection attempts.
    """

    # ── PATTERNS ──────────────────────────────────────────────────────────

    # SQL Injection basics
    SQL_INJECTION = re.compile(
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\b)|([';]|--)",
        re.IGNORECASE,
    )

    # Simple XSS / HTML Injection
    HTML_INJECTION = re.compile(r"<[^>]*script", re.IGNORECASE)

    # Prompt Injection / Control Characters
    # Looking for systemic prompt escape sequences or excessive control chars
    PROMPT_INJECTION = re.compile(
        r"(\[INST\]|\[/INST\]|Assistant:|User:|<\|system\|>|ignore previous instructions)",
        re.IGNORECASE,
    )

    # Control Characters (except newline/tab)
    CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

    @classmethod
    def is_poisoned(cls, text: str) -> bool:
        """
        Scans a string for malicious patterns.
        Returns True if any injection is detected.
        """
        if not text:
            return False

        if cls.SQL_INJECTION.search(text):
            return True
        if cls.HTML_INJECTION.search(text):
            return True
        if cls.PROMPT_INJECTION.search(text):
            return True
        if cls.CONTROL_CHARS.search(text):
            return True

        return False

    @classmethod
    def scan_payload(cls, payload: dict) -> bool:
        """
        Recursively scans a dictionary for malicious strings.
        """
        for key, value in payload.items():
            if isinstance(value, str):
                if cls.is_poisoned(value):
                    return True
            elif isinstance(value, dict):
                if cls.scan_payload(value):
                    return True
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        if cls.is_poisoned(item):
                            return True
                    elif isinstance(item, dict):
                        if cls.scan_payload(item):
                            return True

        return False
