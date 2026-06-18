"""Tao-arm template instantiation (task req 4).

Acceptance/hidden Tao templates are Law payloads carrying the placeholders
``{EMPTY} {INSERT} {MEMBER} {SIZE} {EID} {prim:NAME}`` (prereg A.1). At scoring
time the harness substitutes:

* ``{prim:NAME}``   -> the run's world manifest ``prim_defs[NAME]`` (from
  ``tao-port manifest``) — e.g. ``{prim:intEq}`` -> manifest.prim_defs["intEq"].
* ``{EMPTY} {INSERT} {MEMBER} {SIZE} {EID}`` -> the agent's submitted def ids,
  taken from the run's ``solution.json`` (the agent declares which node id is
  each operation, plus its VocabEntry id ``EID``).

Substitution is whole-string only: a placeholder is a complete JSON string value,
never a substring, so there is no risk of partial/overlapping replacement.
"""

from __future__ import annotations

import json
import pathlib
import re
from typing import Any


_PRIM = re.compile(r"^\{prim:([A-Za-z0-9_]+)\}$")
_DEF_KEYS = ("EMPTY", "INSERT", "MEMBER", "SIZE", "EID")

# the agent's solution declaration that names its submitted def ids.
SOLUTION_FILE = "solution.json"


class SubstitutionError(SystemExit):
    pass


def build_mapping(world_manifest: dict[str, Any], solution: dict[str, Any]) -> dict[str, str]:
    """Combine prim defs (from the manifest) and the agent's def ids (from the
    solution) into a flat placeholder->id mapping. Validates completeness."""
    mapping: dict[str, str] = {}

    prim_defs = world_manifest.get("prim_defs") or {}
    for name, node_id in prim_defs.items():
        mapping[f"{{prim:{name}}}"] = node_id

    sol = {k.lower(): v for k, v in solution.items()}
    # {EID} is the VocabEntry id; the agent declares it as "entry" (preferred) or "eid".
    sources = {"EMPTY": ("empty",), "INSERT": ("insert",), "MEMBER": ("member",),
               "SIZE": ("size",), "EID": ("entry", "eid")}
    for key in _DEF_KEYS:
        val = next((sol[name] for name in sources[key] if sol.get(name)), None)
        if not val:
            raise SubstitutionError(
                f"solution.json missing required def id for '{key}' "
                f"(expected one of {sources[key]})")
        mapping[f"{{{key}}}"] = val
    return mapping


def _resolve(value: str, mapping: dict[str, str]) -> str:
    if value in mapping:
        return mapping[value]
    m = _PRIM.match(value)
    if m:
        raise SubstitutionError(
            f"unknown primitive placeholder {value!r} (not in world manifest)")
    if value.startswith("{") and value.endswith("}") and value[1:-1].isupper():
        raise SubstitutionError(f"unresolved placeholder {value!r}")
    return value


def instantiate(node: Any, mapping: dict[str, str]) -> Any:
    """Recursively substitute placeholder strings throughout a template object."""
    if isinstance(node, str):
        return _resolve(node, mapping)
    if isinstance(node, list):
        return [instantiate(x, mapping) for x in node]
    if isinstance(node, dict):
        return {k: instantiate(v, mapping) for k, v in node.items()}
    return node


def load_solution(mount: pathlib.Path) -> dict[str, Any]:
    path = mount / SOLUTION_FILE
    if not path.exists():
        raise SubstitutionError(f"agent solution declaration not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def render_suite_dir(suite_dir: pathlib.Path, mapping: dict[str, str]) -> list[dict[str, Any]]:
    """Instantiate every ``*.json`` law template in ``suite_dir`` (sorted).

    Returns ``[{"name", "law": <instantiated payload>}]``. ``abstract.json`` is a
    semantics doc, not a law template, and is skipped."""
    rendered: list[dict[str, Any]] = []
    for path in sorted(suite_dir.glob("*.json")):
        if path.name == "abstract.json":
            continue
        template = json.loads(path.read_text(encoding="utf-8"))
        rendered.append({"name": path.stem, "law": instantiate(template, mapping)})
    return rendered
