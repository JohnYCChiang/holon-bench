from __future__ import annotations

import json


def compare_json(actual_text: str, expected_text: str) -> dict:
    return {"ok": actual_text == expected_text, "mismatches": []}
