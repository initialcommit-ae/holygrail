from __future__ import annotations

import re


MAX_TSX_CHARS = 20_000
_REPORT_EXPORT_RE = re.compile(r"export\s+default\s+function\s+Report\s*\(")

# Very cheap denylist checks. Not a real sandbox.
_FORBIDDEN_SUBSTRINGS = [
    "import ",
    "require(",
    "eval(",
    "Function(",
    "fetch(",
    "XMLHttpRequest",
    "WebSocket",
    "localStorage",
    "sessionStorage",
    "document.cookie",
    "navigator.",
    "indexedDB",
]


def validate_generated_tsx(tsx: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(tsx, str) or not tsx.strip():
        return ["TSX is empty"]

    if len(tsx) > MAX_TSX_CHARS:
        errors.append(f"TSX too long (>{MAX_TSX_CHARS} chars)")

    lowered = tsx.lower()
    for s in _FORBIDDEN_SUBSTRINGS:
        if s.lower() in lowered:
            errors.append(f"Forbidden substring detected: {s!r}")

    # Must export default Report
    try:
        if not _REPORT_EXPORT_RE.search(tsx):
            errors.append("TSX must contain: export default function Report(...)")
    except re.error as e:
        errors.append(f"Internal regex error while validating TSX: {e}")

    return errors

