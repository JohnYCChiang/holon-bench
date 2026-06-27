"""Frozen retry simulator. Do not edit — only the policy definition changes."""
from __future__ import annotations

import json
import pathlib


def load_json(name: str) -> dict:
    return json.loads((pathlib.Path(__file__).resolve().parent / name).read_text(encoding="utf-8"))


def simulate(policy: dict, trace: list[str]) -> dict:
    """Replay trace under policy. Returns convergence and attempts used."""
    max_attempts = int(policy.get("max_attempts", 1))
    retryable = set(policy.get("retryable_failures", []))
    used = 0
    for outcome in trace:
        used += 1
        if outcome == "pass":
            return {"converged": True, "attempts_used": used}
        if used >= max_attempts:
            return {"converged": False, "attempts_used": used}
        if outcome not in retryable:
            return {"converged": False, "attempts_used": used}
    return {"converged": False, "attempts_used": used}
