"""Frozen stage scheduler. Do not edit — only the pipeline definition changes."""
from __future__ import annotations

import json
import pathlib


def load_pipeline(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "pipeline.json"
    return json.loads(target.read_text(encoding="utf-8"))


def resolve_order(pipeline: dict) -> list[str]:
    """Deterministic topological order (lowest name first among ready stages).

    Raises ValueError on a cycle or a dependency on an unknown stage.
    """
    stages = pipeline.get("stages", {})
    names = sorted(stages)
    for name in names:
        for dep in stages[name]:
            if dep not in stages:
                raise ValueError(f"stage {name} needs unknown stage {dep}")
    order: list[str] = []
    done: set[str] = set()
    while len(order) < len(names):
        progressed = False
        for name in names:
            if name in done:
                continue
            if all(dep in done for dep in stages[name]):
                order.append(name)
                done.add(name)
                progressed = True
                break
        if not progressed:
            raise ValueError("dependency cycle")
    return order
