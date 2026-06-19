#!/usr/bin/env python3
"""Offline governed-vs-ungoverned smoke for the Holon fs *read* permission path.

This is the read-side sibling of ``holon_fs_governance_smoke.py``. Where that
smoke gates an fs *write* (mutation), this one gates an fs *read* -- the
information boundary / context-exposure case. tao#18 defines the fs-read tiers
``fs.stat | fs.list | fs.read``; holon#11 maps ``read_file`` / ``grep_search`` to
``fs.read`` and ``glob_search`` to ``fs.list``, reusing the same
``tao.fsWitness`` config/witness shape as the write gate.

The witness *decision* logic is identical to the write slice (ungoverned vs
governed-admit vs governed-deny); only the framing differs. A read deny does not
block a mutation -- it blocks the *context exposure*: the file's contents are
never surfaced into the agent's run artifact. The offline ``holon_stub`` models
this with ``HOLON_STUB_FS_KIND=read``, which records an ``fs_read_permission``
check and an ``fs.read`` default effectOp while reusing the same allow/deny path.

All three configurations are driven through the *real* Holon driver -> verifier
-> result -> score pipeline, with no remote API, model endpoint, or compiled
Holon binary. This proves the read-governance metadata and the exposure outcome
flow through the bench end-to-end.

Scenarios (same case, same read, different witness config):

- unconfigured  no witness installed -> ungoverned baseline allow: the read is
  exposed; ``governance_mode == "ungoverned"``; no governance failures.
- governed/admit  witness grants fs.read/fs.list: the read is exposed; passing
  ``fs_read_permission`` check.
- governed/deny   witness denies (missing grant): the context exposure is
  blocked; failing ``fs_read_permission`` check; one governance failure.

After driving the three runs the smoke quantifies the governed-vs-ungoverned
fs-read behavior with ``report.build_governance_comparison`` (the same function
``report.py`` and the fs-write smoke use). The governed runs surface exactly the
one read denial the ungoverned baseline silently allowed (governance-failure
delta ``+1`` over one matched case). The comparison reads only the existing
optional governance fields, so legacy results without them are unaffected.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile

import report
from common import bench_root

CASE_ID = "py-tool-001"
TARGET = "src/tool_errors/runner.py"
ANCHOR = "def run_tool"
# The marker stands in for the file contents the gated read exposes into the
# run artifact. On a deny it never appears -- the context exposure is blocked.
MARKER = "# holon fs-read smoke marker: exposed file contents via gated read.\n"


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
    # Read slice: frame the witness gate as an fs.read context exposure.
    env["HOLON_STUB_FS_KIND"] = "read"
    if witness is not None:
        env["HOLON_STUB_FS_WITNESS"] = witness
    else:
        env.pop("HOLON_STUB_FS_WITNESS", None)

    model = f"holon-fs-read-{label}"
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
            # Never contacted: admit exposes the read into the workspace
            # artifact, deny returns the workflow trace -- neither path reaches
            # the direct fallback.
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
        raise RuntimeError(f"holon_fs_read_governance_smoke: {message}")


def main() -> int:
    root = bench_root(sys.argv[1] if len(sys.argv) > 1 else ".")
    stub = root / "runners" / "holon_stub.py"
    if not stub.is_file():
        raise RuntimeError(f"holon stub missing: {stub}")

    with tempfile.TemporaryDirectory(prefix="holon-bench-fs-read-smoke-") as temp:
        temp_root = pathlib.Path(temp)
        shim = temp_root / "holon"
        shim.write_text(
            f'#!/bin/sh\nexec "{sys.executable}" "{stub}" "$@"\n', encoding="utf-8"
        )
        shim.chmod(0o755)

        # Unconfigured / ungoverned: baseline allow preserved (read exposed).
        ungov_art, ungov_res, ungov_score = run_scenario(
            root, shim, temp_root, "ungoverned", witness="none"
        )
        check(
            MARKER.strip() in ungov_art,
            "ungoverned did not preserve baseline allow (read not exposed)",
        )
        check(
            ungov_res.get("governance_mode") == "ungoverned",
            "ungoverned run was not labeled ungoverned in the result",
        )
        check(
            ungov_score.get("governance_failure_count") == 0,
            "ungoverned run unexpectedly recorded a governance failure",
        )

        # Governed + admit: witness grants fs.read/fs.list -> read exposed.
        admit_art, admit_res, admit_score = run_scenario(
            root, shim, temp_root, "admit", witness="admit"
        )
        check(MARKER.strip() in admit_art, "governed/admit did not allow the fs read")
        check(
            admit_res.get("governance_mode") == "governed",
            "governed/admit run was not labeled governed",
        )
        admit_checks = {c["name"]: c for c in admit_res.get("governance_checks") or []}
        check(
            admit_checks.get("fs_read_permission", {}).get("passed") is True,
            "governed/admit did not record a passing fs_read_permission check",
        )
        check(
            admit_score.get("governance_failure_count") == 0,
            "governed/admit unexpectedly recorded a governance failure",
        )

        # Governed + deny: witness denies (missing grant) -> exposure blocked.
        deny_art, deny_res, deny_score = run_scenario(
            root, shim, temp_root, "deny", witness="deny"
        )
        check(
            MARKER.strip() not in deny_art,
            "governed/deny did NOT block the context exposure (baseline leaked through)",
        )
        check(
            deny_res.get("governance_mode") == "governed",
            "governed/deny run was not labeled governed",
        )
        deny_checks = {c["name"]: c for c in deny_res.get("governance_checks") or []}
        check(
            deny_checks.get("fs_read_permission", {}).get("passed") is False,
            "governed/deny did not record a failing fs_read_permission check",
        )
        check(
            "context exposure blocked" in deny_checks.get("fs_read_permission", {}).get("detail", ""),
            "governed/deny did not frame the denial as a blocked context exposure",
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

        # Quantify the governed-vs-ungoverned fs-read behavior from the three
        # scored runs, reusing report.build_governance_comparison so this read
        # slice is measured exactly as a full benchmark run would surface it. No
        # new schema or scoring path: the comparison reads the existing optional
        # governance fields and is skipped entirely when they are absent.
        comparison = report.build_governance_comparison(
            [ungov_score, admit_score, deny_score]
        )
        check(comparison is not None, "no governance comparison was produced")
        check(
            comparison["matched_case_count"] == 1,
            "read slice did not match the same case across governed and ungoverned",
        )
        governed_metrics = comparison["governed"]
        ungoverned_metrics = comparison["ungoverned"]
        check(
            ungoverned_metrics["case_count"] == 1
            and governed_metrics["case_count"] == 2,
            "read slice did not partition into one ungoverned and two governed runs",
        )
        # The measurable governed-vs-ungoverned fs-read delta: governance
        # surfaces exactly the one read denial (the deny scenario) that the
        # ungoverned baseline silently allowed.
        check(
            ungoverned_metrics["governance_failure_count"] == 0,
            "ungoverned baseline unexpectedly recorded a governance failure",
        )
        check(
            governed_metrics["governance_failure_count"] == 1
            and governed_metrics["cases_with_governance_failure"] == 1,
            "governed runs did not record exactly the one fs-read governance failure",
        )
        deltas = comparison["deltas"]
        check(
            deltas["governance_failure_count"] == 1,
            "governed-minus-ungoverned governance failure delta was not quantified as +1",
        )

    print(
        "holon_fs_read_governance_smoke: ok "
        "(ungoverned allow vs governed admit/deny context exposure, no remote "
        f"APIs; governed-minus-ungoverned fs-read governance-failure delta "
        f"{deltas['governance_failure_count']:+d} over "
        f"{comparison['matched_case_count']} matched case)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
