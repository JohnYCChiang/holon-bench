"""Frozen workflow engine. Do not edit — only the workflow definition changes."""
from __future__ import annotations

import json
import pathlib


def load_workflow(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "workflow.json"
    return json.loads(target.read_text(encoding="utf-8"))


def evaluate(workflow: dict, submission: dict) -> str:
    """Return 'accept' iff every gate of every stage is truthy in submission."""
    for stage in workflow.get("stages", []):
        for gate in stage.get("gates", []):
            if not submission.get(gate, False):
                return "reject"
    return "accept"
