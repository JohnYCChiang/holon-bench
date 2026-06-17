#!/usr/bin/env python3
"""Builder for Holon Tao fs EffectOp witness files (real config surface).

Holon#7 (merged in ``taichi/holon`` PR #8, merge commit ``394a734``) adds the
external config surface that lets a ``TaoEffectOpWitnessSource`` be installed
from *outside* the process, so the fs permission gate (holon#5 / tao#5) can be
driven by a real, on-disk witness file instead of being modeled in-process.

Config surface (exactly as Holon consumes it):

- ``HOLON_TAO_FS_WITNESS=<path>`` env var points at the witness file. An empty
  value means *unset*; the env wins over the settings key.
- ``tao.fsWitness.path`` (non-empty string) in Holon ``settings.json`` is the
  settings-file equivalent of the env var.
- A relative witness path resolves against the process CWD.
- Unset => legacy ungated behavior (no witness source installed).
- Configured but malformed => fail closed.
- Configured and well-formed but with no matching grant row => missing-grant
  deny once the source is installed.

Witness file shape::

    { "grants": [ { "effectOp", "resource"?, "decision",
                    "resultType"?, "row"?, "reason"?, "at"? } ] }

- ``effectOp`` is one of ``fs.create | fs.overwrite | fs.edit | fs.delete``.
- ``decision`` is ``admit`` or ``deny``.
- an ``admit`` grant requires ``resultType``; a ``deny`` grant requires
  ``reason``.

This module only *builds and writes* witness files (and a matching
``settings.json`` snippet). It performs no network or model calls and does not
require a compiled Holon binary, so it is safe to import and unit-test in CI.
The real-binary smoke (``holon_real_fs_governance_smoke.py``) uses it to lay
down the unconfigured / governed-admit / governed-deny witness files.
"""
from __future__ import annotations

import json
import pathlib
from typing import Any

EFFECT_OPS = ("fs.create", "fs.overwrite", "fs.edit", "fs.delete")
DECISIONS = ("admit", "deny")


class WitnessError(ValueError):
    """Raised when a grant violates the Holon witness contract."""


def grant(
    effect_op: str,
    decision: str,
    *,
    resource: str | None = None,
    result_type: str | None = None,
    row: Any | None = None,
    reason: str | None = None,
    at: str | None = None,
) -> dict:
    """Build one witness grant, enforcing the Holon contract.

    Mirrors Holon's own validation so a malformed grant fails *here* (loudly,
    offline) rather than only being rejected fail-closed by the runtime:

    - ``effect_op`` must be a known fs EffectOp.
    - ``decision`` must be ``admit`` or ``deny``.
    - ``admit`` requires ``result_type``; ``deny`` requires ``reason``.
    """
    if effect_op not in EFFECT_OPS:
        raise WitnessError(
            f"unknown effectOp {effect_op!r}; expected one of {EFFECT_OPS}"
        )
    if decision not in DECISIONS:
        raise WitnessError(
            f"unknown decision {decision!r}; expected one of {DECISIONS}"
        )
    if decision == "admit" and not result_type:
        raise WitnessError("an admit grant requires a non-empty resultType")
    if decision == "deny" and not reason:
        raise WitnessError("a deny grant requires a non-empty reason")

    built: dict = {"effectOp": effect_op, "decision": decision}
    if resource is not None:
        built["resource"] = resource
    if result_type is not None:
        built["resultType"] = result_type
    if row is not None:
        built["row"] = row
    if reason is not None:
        built["reason"] = reason
    if at is not None:
        built["at"] = at
    return built


def document(grants: list[dict]) -> dict:
    """Wrap grants in the top-level ``{ "grants": [...] }`` witness document."""
    return {"grants": list(grants)}


def write_witness(path: pathlib.Path, grants: list[dict]) -> pathlib.Path:
    """Write a witness document to ``path`` and return it (deterministic JSON)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document(grants), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def admit_grant(effect_op: str, resource: str, *, result_type: str = "Patch") -> dict:
    """A grant that admits ``effect_op`` on ``resource`` (carries resultType)."""
    return grant(
        effect_op,
        "admit",
        resource=resource,
        result_type=result_type,
    )


def deny_grant(effect_op: str, resource: str, *, reason: str | None = None) -> dict:
    """A grant that explicitly denies ``effect_op`` on ``resource``."""
    return grant(
        effect_op,
        "deny",
        resource=resource,
        reason=reason or f"witness denies {effect_op} on {resource}",
    )


def settings_snippet(witness_path: pathlib.Path) -> dict:
    """The ``tao.fsWitness.path`` settings-file equivalent of the env var.

    Holon reads the env var first; this snippet documents (and lets callers
    write) the settings-file surface for the same gate.
    """
    return {"tao": {"fsWitness": {"path": str(witness_path)}}}
