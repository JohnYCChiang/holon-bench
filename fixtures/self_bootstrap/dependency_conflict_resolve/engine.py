"""Frozen dependency consistency checker. Do not edit — only the lockfile changes."""
from __future__ import annotations

import json
import pathlib


def load_deps(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "deps.json"
    return json.loads(target.read_text(encoding="utf-8"))


def _ver(v: str) -> tuple:
    return tuple(int(x) for x in v.split("."))


def satisfies(version: str, constraint: str) -> bool:
    for part in constraint.split(","):
        part = part.strip()
        for op in (">=", "<=", "==", ">", "<"):
            if part.startswith(op):
                target = _ver(part[len(op):])
                cur = _ver(version)
                if op == ">=" and not cur >= target:
                    return False
                if op == "<=" and not cur <= target:
                    return False
                if op == ">" and not cur > target:
                    return False
                if op == "<" and not cur < target:
                    return False
                if op == "==" and not cur == target:
                    return False
                break
    return True


def violations(cfg: dict) -> list:
    selected = cfg.get("selected", {})
    available = cfg.get("available", {})
    requirements = cfg.get("requirements", {})
    out: list = []
    for pkg, ver in selected.items():
        if ver not in available.get(pkg, []):
            out.append(f"{pkg}@{ver} not in available")
    for svc, needs in requirements.items():
        for dep, constraint in needs.items():
            ver = selected.get(dep)
            if ver is None or not satisfies(ver, constraint):
                out.append(f"{svc} requires {dep}{constraint}, selected {ver}")
    return out


def is_consistent(cfg: dict) -> bool:
    return not violations(cfg)
