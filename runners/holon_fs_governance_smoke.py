#!/usr/bin/env python3
"""Offline governed-vs-ungoverned smoke for the Holon fs permission path.

Holon#5 (merge e00cb8b) gates one fs permission path through a Tao
``TaoEffectOpWitnessSource`` when one is installed, while preserving the legacy
behavior when it is not (tao#5 defines the ``EffectOp`` witness contract). The
compiled Holon CLI does not yet expose an external config surface for installing
a witness source, so this smoke models the witness decision in the offline
``holon_stub`` and drives all three configurations through the *real* Holon
driver -> verifier -> result -> score pipeline. This proves the governance
metadata and the fs outcome flow through the bench end-to-end, with no remote
API, model endpoint, or compiled Holon binary.

See ``.claude/tasks/holon-tao-witness-gate.md`` for what is measured here and
what remains real-CLI wiring. The generic governance surfacing smoke is
``holon_smoke.py``; this one isolates the fs EffectOp gate specifically.

Scenarios (same case, same edit, different witness config):

- unconfigured  no witness installed -> ungoverned baseline allow: fs write
  happens; ``governance_mode == "ungoverned"``; no governance failures.
- governed/admit  witness grants the fs EffectOp: fs write happens; passing
  ``fs_permission`` check.
- governed/deny   witness denies (missing grant): fs write is blocked; failing
  ``fs_permission`` check; one governance failure.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile

from common import bench_root

CASE_ID = "py-tool-001"
TARGET = "src/tool_errors/runner.py"
ANCHOR = "def run_tool"
MARKER = "# holon fs-witness smoke marker: gated owned-file change via stub.\n"


def run(command: list[str], root: pathlib.Path, env: dict[str, str]) -> None:
    completed = subprocess.run(
        command, cwd=root, text=True, capture_output=True, check=False, env=env
    )
    if completed.returncode not in (0, 1):
        # 0 = case passed, 1 = case failed its verifier (expected on a deny).
        # Anything else is a harness/crash failure we must surface.
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )


def run_scenario(
    root: pathlib.Path,
    shim: pathlib.Path,
    temp_root: pathlib.Path,
    label: str,
    witness: str | None,
) -> tuple[str, dict, dict]:
    artifact = temp_root / f"{label}_artifact.txt"
    result = temp_root / f"{label}_result.json"
    score = temp_root / f"{label}_score.json"

    env = os.environ.copy()
    env["HOLON_BIN"] = str(shim)
    env["HOLON_STUB_TARGET"] = TARGET
    env["HOLON_STUB_ANCHOR"] = ANCHOR
    env["HOLON_STUB_MARKER"] = MARKER
    env["HOLON_STUB_CASE"] = CASE_ID
    if witness is not None:
        env["HOLON_STUB_FS_WITNESS"] = witness
    else:
        env.pop("HOLON_STUB_FS_WITNESS", None)

    model = f"holon-fs-{label}"
    run(
        [
            sys.executable,
            str(root / "runners" / "run_model_case.py"),
            CASE_ID,
            "--model",
            model,
            "--driver",
            "holon-cli",
            "--protocol",
            "artifact",
            # Never contacted: admit edits the workspace, deny returns the
            # workflow trace -- neither path reaches the direct fallback.
            "--endpoint",
            "http://127.0.0.1:1/v1",
            "--bench-root",
            str(root),
            "--out",
            str(artifact),
        ],
        root,
        env,
    )
    run(
        [
            sys.executable,
            str(root / "runners" / "run_case.py"),
            CASE_ID,
            "--model",
            model,
            "--artifact-file",
            str(artifact),
            "--bench-root",
            str(root),
            "--work-root",
            str(temp_root / f"{label}_work"),
            "--out",
            str(result),
        ],
        root,
        env,
    )
    run(
        [
            sys.executable,
            str(root / "runners" / "score_case.py"),
            str(result),
            "--bench-root",
            str(root),
            "--out",
            str(score),
        ],
        root,
        env,
    )
    return (
        artifact.read_text(encoding="utf-8"),
        json.loads(result.read_text(encoding="utf-8")),
        json.loads(score.read_text(encoding="utf-8")),
    )


def check(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(f"holon_fs_governance_smoke: {message}")


def main() -> int:
    root = bench_root(sys.argv[1] if len(sys.argv) > 1 else ".")
    stub = root / "runners" / "holon_stub.py"
    if not stub.is_file():
        raise RuntimeError(f"holon stub missing: {stub}")

    with tempfile.TemporaryDirectory(prefix="holon-bench-fs-smoke-") as temp:
        temp_root = pathlib.Path(temp)
        shim = temp_root / "holon"
        shim.write_text(
            f'#!/bin/sh\nexec "{sys.executable}" "{stub}" "$@"\n', encoding="utf-8"
        )
        shim.chmod(0o755)

        # Unconfigured / ungoverned: baseline allow preserved.
        ungov_art, ungov_res, ungov_score = run_scenario(
            root, shim, temp_root, "ungoverned", witness="none"
        )
        check(MARKER.strip() in ungov_art, "ungoverned did not preserve baseline allow")
        check(
            ungov_res.get("governance_mode") == "ungoverned",
            "ungoverned run was not labeled ungoverned in the result",
        )
        check(
            ungov_score.get("governance_failure_count") == 0,
            "ungoverned run unexpectedly recorded a governance failure",
        )

        # Governed + admit: witness grants the fs EffectOp.
        admit_art, admit_res, admit_score = run_scenario(
            root, shim, temp_root, "admit", witness="admit"
        )
        check(MARKER.strip() in admit_art, "governed/admit did not allow the fs write")
        check(
            admit_res.get("governance_mode") == "governed",
            "governed/admit run was not labeled governed",
        )
        admit_checks = {c["name"]: c for c in admit_res.get("governance_checks") or []}
        check(
            admit_checks.get("fs_permission", {}).get("passed") is True,
            "governed/admit did not record a passing fs_permission check",
        )
        check(
            admit_score.get("governance_failure_count") == 0,
            "governed/admit unexpectedly recorded a governance failure",
        )

        # Governed + deny: witness denies (missing grant) -> fs write blocked.
        deny_art, deny_res, deny_score = run_scenario(
            root, shim, temp_root, "deny", witness="deny"
        )
        check(
            MARKER.strip() not in deny_art,
            "governed/deny did NOT block the fs write (baseline leaked through)",
        )
        check(
            deny_res.get("governance_mode") == "governed",
            "governed/deny run was not labeled governed",
        )
        deny_checks = {c["name"]: c for c in deny_res.get("governance_checks") or []}
        check(
            deny_checks.get("fs_permission", {}).get("passed") is False,
            "governed/deny did not record a failing fs_permission check",
        )
        check(
            deny_score.get("governance_failure_count") == 1,
            "governed/deny did not record exactly one governance failure",
        )
        chain = deny_res.get("tao_truth_chain") or {}
        check(
            chain.get("subject_id") == f"case::{CASE_ID}",
            "governed/deny did not surface the Tao truth chain",
        )

    print(
        "holon_fs_governance_smoke: ok "
        "(ungoverned allow vs governed admit/deny, no remote APIs)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
