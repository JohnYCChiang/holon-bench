#!/usr/bin/env python3
"""Offline stand-in for the Holon CLI, used by the Holon smoke path and tests.

The real Holon driver shells out to a compiled ``holon`` binary that performs
model calls and edits the workspace. That binary is unavailable in CI and would
require remote APIs. This stub mimics only the parts of the Holon contract the
benchmark driver depends on:

- it edits an owned file in the workspace (deterministically), so the driver can
  collect a normalized artifact/diff exactly as it would from real Holon output;
- when asked, it writes ``.holon/governance.json`` with the optional governance
  metadata (governance_mode / governance_checks / tao_truth_chain) that the
  driver surfaces "when present";
- it prints a Holon-style JSON trace line so graph-tool detection has input.

It performs no network or model calls. Behavior is driven entirely by env vars
so the stub stays case-agnostic:

- ``HOLON_STUB_TARGET``      workspace-relative file to edit (required to edit)
- ``HOLON_STUB_MARKER``      text inserted into the target (default: a comment)
- ``HOLON_STUB_ANCHOR``      if set, marker is inserted before this text;
                             otherwise the marker is prepended to the file
- ``HOLON_STUB_GOVERNANCE``  ``"1"`` to emit ``.holon/governance.json``
- ``HOLON_STUB_CASE``        case id recorded in the tao_truth_chain subject id

Tao fs EffectOp witness model (``HOLON_STUB_FS_WITNESS``)
--------------------------------------------------------
When ``HOLON_STUB_FS_WITNESS`` is set, the stub models the one fs permission
path that the Holon runtime gates when a ``TaoEffectOpWitnessSource`` is
installed (holon#5 / tao#5). It overrides the generic governance path above and
makes the governed-vs-ungoverned behavioral difference observable offline:

- unset / ``none`` / ``absent``  -> no witness source installed: the legacy,
  *ungoverned* path. Baseline allow — the fs write happens and an ``ungoverned``
  governance record (no Tao checks) is emitted so the run is comparable.
- ``admit`` / ``allow`` / ``grant`` -> witness *admits* the fs EffectOp: the fs
  write happens and a passing ``fs_permission`` check is recorded.
- ``deny`` / ``missing`` (or any unknown value, fail-closed) -> witness *denies*
  (missing grant): the fs write is blocked and a failing ``fs_permission`` check
  is recorded, with no edit applied.

Real witness file gate (``HOLON_TAO_FS_WITNESS``)
-------------------------------------------------
When ``HOLON_TAO_FS_WITNESS`` is set to a path, the stub stands in for the real
Holon config surface (holon#7, merge ``394a734``): it reads the on-disk witness
file (``{ grants: [...] }``) and applies the same gate the compiled binary would.
This lets the *real-binary* smoke be rehearsed offline against the same witness
files it would feed a real ``holon`` binary. The contract mirrored here:

- unset / empty                 -> legacy ungated path (no witness source), as if
  ``HOLON_TAO_FS_WITNESS`` were absent. The generic path runs.
- a grant matching the fs EffectOp with ``decision == "admit"`` and a
  ``resultType`` -> admit: the fs write happens.
- a malformed / unreadable witness file, a grant missing its required field, or
  no matching grant row -> deny (fail-closed / missing grant): the write is
  blocked.

``HOLON_TAO_FS_WITNESS`` wins over ``HOLON_STUB_FS_WITNESS`` (env-over-model),
matching Holon's env-over-settings precedence. The matched fs EffectOp defaults
to ``fs.edit`` and can be overridden with ``HOLON_STUB_FS_EFFECT_OP``.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys


def apply_change(cwd: pathlib.Path) -> None:
    target = os.environ.get("HOLON_STUB_TARGET")
    if not target:
        return
    path = cwd / target
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    marker = os.environ.get("HOLON_STUB_MARKER", "# holon offline stub change\n")
    if marker in text:
        return
    anchor = os.environ.get("HOLON_STUB_ANCHOR")
    if anchor and anchor in text:
        text = text.replace(anchor, marker + anchor, 1)
    else:
        text = marker + text
    path.write_text(text, encoding="utf-8")


def write_governance(cwd: pathlib.Path) -> None:
    if os.environ.get("HOLON_STUB_GOVERNANCE") != "1":
        return
    case_id = os.environ.get("HOLON_STUB_CASE", "smoke")
    holon_dir = cwd / ".holon"
    holon_dir.mkdir(exist_ok=True)
    governance = {
        "governance_mode": "governed",
        "governance_checks": [
            {
                "name": "scope_guard",
                "passed": True,
                "tao_fact_id": f"fact-scope-{case_id}",
                "detail": "edits stayed within allowed paths",
            },
            {
                "name": "verifier_gate",
                "passed": True,
                "detail": "verifier was run, not bypassed",
            },
        ],
        "tao_truth_chain": {
            "subject_id": f"case::{case_id}",
            "fact_kind": "implementation",
            "fact_id": f"fact-impl-{case_id}",
            "artifact_ids": [f"artifact-{case_id}"],
            "verifier_input_ids": [f"verifier-{case_id}"],
        },
    }
    (holon_dir / "governance.json").write_text(
        json.dumps(governance, indent=2), encoding="utf-8"
    )


def fs_witness_decision() -> tuple[str | None, str | None]:
    """Resolve the Tao fs EffectOp witness gate from ``HOLON_STUB_FS_WITNESS``.

    Returns ``(mode, decision)``:

    - ``(None, None)``        the var is unset: not in fs-witness mode, so the
      stub's generic governance path runs instead (behavior unchanged).
    - ``("ungoverned", "admit")``  no witness installed: baseline allow.
    - ``("governed", "admit")``    witness grants the fs EffectOp.
    - ``("governed", "deny")``     witness denies / missing grant (fail-closed
      for unknown values).
    """
    raw = os.environ.get("HOLON_STUB_FS_WITNESS")
    if raw is None:
        return None, None
    value = raw.strip().lower()
    if value in ("", "none", "absent", "unconfigured", "legacy"):
        return "ungoverned", "admit"
    if value in ("admit", "allow", "grant", "granted"):
        return "governed", "admit"
    # deny / missing / missing_grant / denied and anything unrecognized fail closed.
    return "governed", "deny"


FS_EFFECT_OPS = ("fs.create", "fs.overwrite", "fs.edit", "fs.delete")


def real_witness_decision() -> tuple[str | None, str | None]:
    """Resolve the real fs EffectOp witness gate from ``HOLON_TAO_FS_WITNESS``.

    Stands in for the compiled Holon binary's gate (holon#7, merge ``394a734``)
    by reading the on-disk witness file and applying the same contract. Returns
    ``(mode, decision)``:

    - ``(None, None)``          the var is unset/empty: no witness source, so the
      stub falls through to its other paths (legacy behavior unchanged).
    - ``("governed", "admit")``  a matching grant admits the fs EffectOp.
    - ``("governed", "deny")``   missing/malformed witness, missing required
      grant field, or no matching grant row (all fail-closed).
    """
    raw = os.environ.get("HOLON_TAO_FS_WITNESS")
    if raw is None or raw.strip() == "":
        # Empty means unset; env-over-settings precedence is the caller's job.
        return None, None
    path = pathlib.Path(raw)
    if not path.is_absolute():
        # A relative witness path resolves against the process CWD.
        path = pathlib.Path.cwd() / path
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        # Configured but malformed/unreadable => fail closed.
        return "governed", "deny"
    grants = data.get("grants") if isinstance(data, dict) else None
    if not isinstance(grants, list):
        return "governed", "deny"

    effect_op = os.environ.get("HOLON_STUB_FS_EFFECT_OP", "fs.edit")
    target = os.environ.get("HOLON_STUB_TARGET", "")
    for grant in grants:
        if not isinstance(grant, dict):
            continue
        if grant.get("effectOp") != effect_op:
            continue
        resource = grant.get("resource")
        if resource is not None and resource != target:
            continue
        decision = grant.get("decision")
        if decision == "admit" and grant.get("resultType"):
            return "governed", "admit"
        if decision == "deny" and grant.get("reason"):
            return "governed", "deny"
        # Matching row but missing its required field => fail closed.
        return "governed", "deny"
    # No matching grant row => missing-grant deny.
    return "governed", "deny"


def write_fs_governance(cwd: pathlib.Path, mode: str, decision: str) -> None:
    case_id = os.environ.get("HOLON_STUB_CASE", "smoke")
    target = os.environ.get("HOLON_STUB_TARGET", "")
    holon_dir = cwd / ".holon"
    holon_dir.mkdir(exist_ok=True)
    if mode == "ungoverned":
        # Legacy/unconfigured: no Tao EffectOp witness ran, so no governance
        # checks are recorded. The baseline-allow behavior is proven by the
        # applied fs edit, not by a check.
        governance: dict = {
            "governance_mode": "ungoverned",
            "governance_checks": [],
        }
    else:
        admitted = decision == "admit"
        governance = {
            "governance_mode": "governed",
            "governance_checks": [
                {
                    "name": "fs_permission",
                    "passed": admitted,
                    "tao_fact_id": f"fact-fs-{case_id}",
                    "detail": (
                        f"Tao EffectOp witness admitted fs write to {target}"
                        if admitted
                        else f"Tao EffectOp witness denied fs write to {target} "
                        "(missing grant)"
                    ),
                }
            ],
            "tao_truth_chain": {
                "subject_id": f"case::{case_id}",
                "fact_kind": "effect_op_witness",
                "fact_id": f"fact-fs-{case_id}",
                "artifact_ids": [f"artifact-{case_id}"],
                "verifier_input_ids": [f"witness-{case_id}"],
            },
        }
    (holon_dir / "governance.json").write_text(
        json.dumps(governance, indent=2), encoding="utf-8"
    )


def main() -> int:
    cwd = pathlib.Path.cwd()
    real_mode, real_decision = real_witness_decision()
    if real_mode is not None:
        # Real config-surface path: gate read from the on-disk witness file
        # (HOLON_TAO_FS_WITNESS), exactly as the compiled binary would.
        if real_decision == "admit":
            apply_change(cwd)
        write_fs_governance(cwd, real_mode, real_decision)
        print(json.dumps({"graph_tool_calls": ["RecallMemory"]}))
        return 0
    fs_mode, fs_decision = fs_witness_decision()
    if fs_mode is not None:
        # Tao fs EffectOp witness path: the gate decides whether the fs write
        # is allowed before it happens.
        if fs_decision == "admit":
            apply_change(cwd)
        write_fs_governance(cwd, fs_mode, fs_decision)
    else:
        apply_change(cwd)
        write_governance(cwd)
    # Holon-style trace line so the driver's graph-tool detection has input.
    print(json.dumps({"graph_tool_calls": ["RecallMemory"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
