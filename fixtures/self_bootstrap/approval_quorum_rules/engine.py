"""Frozen approval-quorum engine. Do not edit — only the quorum rules change."""
from __future__ import annotations

import json
import pathlib


def load_quorum(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "quorum.json"
    return json.loads(target.read_text(encoding="utf-8"))


def _eligible(change: dict, allow_self: bool) -> list[dict]:
    author = change.get("author")
    if allow_self:
        return list(change.get("approvals", []))
    return [a for a in change.get("approvals", []) if a.get("user") != author]


def is_approved(config: dict, change: dict) -> bool:
    """True when the change meets its rule's count and required-role quorum."""
    rules = config.get("rules", {})
    rule = rules.get(change.get("type"), config.get("default_rule", {}))
    approvals = _eligible(change, bool(rule.get("allow_self_approval", False)))
    if len(approvals) < int(rule.get("min_approvals", 1)):
        return False
    roles = {a.get("role") for a in approvals}
    return all(required in roles for required in rule.get("required_roles", []))
