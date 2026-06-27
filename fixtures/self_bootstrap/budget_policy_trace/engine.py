"""Frozen cost-budget simulator. Do not edit — only the budget policy changes."""
from __future__ import annotations

import json
import pathlib


def load_json(name: str) -> dict:
    return json.loads((pathlib.Path(__file__).resolve().parent / name).read_text(encoding="utf-8"))


def run_plan(budget: dict, tasks: list[str]) -> dict:
    """Execute tasks in order, charging each task's cost until the budget is exceeded."""
    max_total = int(budget.get("max_total_cost", 0))
    costs = budget.get("task_cost", {})
    default_cost = int(budget.get("default_cost", 1))
    spent = 0
    for task in tasks:
        spent += int(costs.get(task, default_cost))
        if spent > max_total:
            return {"completed": False, "spent": spent}
    return {"completed": True, "spent": spent}
