"""Frozen log redactor. Do not edit — only the redaction field list changes."""
from __future__ import annotations

import json
import pathlib


def load_config(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "redaction.json"
    return json.loads(target.read_text(encoding="utf-8"))


def redact(config: dict, record: dict) -> dict:
    """Return a copy of record with configured fields masked as '***'."""
    fields = set(config.get("redact_fields", []))
    return {key: ("***" if key in fields else value) for key, value in record.items()}
