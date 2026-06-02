from __future__ import annotations


def redact_output(text: str, preview_lines: int = 3) -> dict:
    lines = text.splitlines()
    return {
        "redacted": text,
        "line_count": len(lines),
        "byte_count": len(text.encode("utf-8")),
        "redaction_count": 0,
        "preview": "\n".join(lines[:preview_lines]),
    }
