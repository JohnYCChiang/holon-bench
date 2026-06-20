#!/usr/bin/env python3
"""Shared harness for the offline governed-vs-ungoverned governance smokes.

The fs-write, fs-read, process-control, and network-egress smokes are the *same*
end-to-end experiment over different Tao capability classes: drive the same case
through the real Holon driver -> verifier -> result -> score pipeline under three
witness configurations (unconfigured / governed-admit / governed-deny), then feed
the three scores back through ``report.build_governance_comparison`` and assert the
governed runs surface exactly the one denial the ungoverned baseline silently
allowed (governance-failure delta ``+1`` over one matched case). The offline
``holon_stub`` models each witness decision; no remote API, model endpoint, or
compiled Holon binary is contacted, and (for process/network) no real process or
socket is ever touched.

Each capability slice differs only in a handful of parameters captured by
[`GovernanceSmokeSpec`]: which ``HOLON_STUB_*_WITNESS`` env var installs the
witness, any extra framing env (``HOLON_STUB_FS_KIND`` / ``HOLON_STUB_PROCESS_OP``
/ ``HOLON_STUB_NET_OP``), the governance check name the gate records, the marker
that stands in for the gated effect, and the human-summary wording. A per-slice
runner is then ~a dozen lines: build a spec and call
[`run_governance_smoke`].

Output contract: the final line is ``"{smoke_name}: ok (...; ... governance-failure
delta +1 over 1 matched case)"``. The ``{smoke_name}: ok`` token and the
``delta +N over M matched case`` suffix are parsed by
``holon_governance_matrix.py``, so they are preserved exactly.
"""
from __future__ import annotations

import dataclasses
import json
import os
import pathlib
import subprocess
import sys
import tempfile

import report
from common import bench_root

# Constants shared by every governance slice (identical across all four smokes).
CASE_ID = "py-tool-001"
TARGET = "src/tool_errors/runner.py"
ANCHOR = "def run_tool"


@dataclasses.dataclass(frozen=True)
class GovernanceSmokeSpec:
    """One capability slice's parameters for the shared governance smoke."""

    # Smoke identity: used for the check prefix and the parsed "{name}: ok" line.
    smoke_name: str
    # The HOLON_STUB_*_WITNESS env var that installs the modeled witness.
    witness_env: str
    # The governance check name the gate records (e.g. "fs_permission").
    check_name: str
    # Inert marker standing in for the gated effect; absent from the artifact on a
    # deny (the effect is blocked).
    marker: str
    # Per-slice run-model label prefix and temp-dir prefix.
    model_prefix: str
    temp_prefix: str
    # Human-summary middle clause and the delta noun, kept verbatim so the parsed
    # output line is byte-identical to the pre-consolidation smokes.
    summary_clause: str
    delta_label: str
    # Phrase the governed/deny check detail must contain, or None to skip the
    # detail assertion (the fs-write slice asserts no detail phrase).
    deny_detail_phrase: str | None = None
    # Extra framing env applied to every scenario (e.g. HOLON_STUB_FS_KIND=read).
    extra_env: tuple[tuple[str, str], ...] = ()
    case_id: str = CASE_ID
    target: str = TARGET
    anchor: str = ANCHOR


def _run(command: list[str], root: pathlib.Path, env: dict[str, str]) -> None:
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


def _run_scenario(
    spec: GovernanceSmokeSpec,
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
    env["HOLON_STUB_TARGET"] = spec.target
    env["HOLON_STUB_ANCHOR"] = spec.anchor
    env["HOLON_STUB_MARKER"] = spec.marker
    env["HOLON_STUB_CASE"] = spec.case_id
    for key, value in spec.extra_env:
        env[key] = value
    if witness is not None:
        env[spec.witness_env] = witness
    else:
        env.pop(spec.witness_env, None)

    model = f"{spec.model_prefix}-{label}"
    _run(
        [
            sys.executable,
            str(root / "runners" / "run_model_case.py"),
            spec.case_id,
            "--model",
            model,
            "--driver",
            "holon-cli",
            "--protocol",
            "artifact",
            # Never contacted: admit records the modeled effect in the workspace,
            # deny returns the workflow trace -- neither path reaches the direct
            # fallback.
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
    _run(
        [
            sys.executable,
            str(root / "runners" / "run_case.py"),
            spec.case_id,
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
    _run(
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


def run_governance_smoke(spec: GovernanceSmokeSpec, argv: list[str] | None = None) -> int:
    """Drive one capability slice's three-scenario governance smoke.

    Returns 0 on success; raises ``RuntimeError`` (prefixed with the smoke name)
    on any failed assertion, matching the pre-consolidation per-smoke behavior.
    """
    args = sys.argv if argv is None else argv
    root = bench_root(args[1] if len(args) > 1 else ".")
    stub = root / "runners" / "holon_stub.py"
    if not stub.is_file():
        raise RuntimeError(f"holon stub missing: {stub}")

    def check(condition: bool, message: str) -> None:
        if not condition:
            raise RuntimeError(f"{spec.smoke_name}: {message}")

    marker = spec.marker.strip()

    with tempfile.TemporaryDirectory(prefix=spec.temp_prefix) as temp:
        temp_root = pathlib.Path(temp)
        shim = temp_root / "holon"
        shim.write_text(
            f'#!/bin/sh\nexec "{sys.executable}" "{stub}" "$@"\n', encoding="utf-8"
        )
        shim.chmod(0o755)

        # Unconfigured / ungoverned: baseline allow preserved.
        ungov_art, ungov_res, ungov_score = _run_scenario(
            spec, root, shim, temp_root, "ungoverned", witness="none"
        )
        check(
            marker in ungov_art,
            "ungoverned did not preserve baseline allow (modeled effect not recorded)",
        )
        check(
            ungov_res.get("governance_mode") == "ungoverned",
            "ungoverned run was not labeled ungoverned in the result",
        )
        check(
            ungov_score.get("governance_failure_count") == 0,
            "ungoverned run unexpectedly recorded a governance failure",
        )

        # Governed + admit: witness grants the EffectOp.
        admit_art, admit_res, admit_score = _run_scenario(
            spec, root, shim, temp_root, "admit", witness="admit"
        )
        check(marker in admit_art, "governed/admit did not allow the modeled effect")
        check(
            admit_res.get("governance_mode") == "governed",
            "governed/admit run was not labeled governed",
        )
        admit_checks = {c["name"]: c for c in admit_res.get("governance_checks") or []}
        check(
            admit_checks.get(spec.check_name, {}).get("passed") is True,
            f"governed/admit did not record a passing {spec.check_name} check",
        )
        check(
            admit_score.get("governance_failure_count") == 0,
            "governed/admit unexpectedly recorded a governance failure",
        )

        # Governed + deny: witness denies (missing grant) -> effect blocked.
        deny_art, deny_res, deny_score = _run_scenario(
            spec, root, shim, temp_root, "deny", witness="deny"
        )
        check(
            marker not in deny_art,
            "governed/deny did NOT block the modeled effect (baseline leaked through)",
        )
        check(
            deny_res.get("governance_mode") == "governed",
            "governed/deny run was not labeled governed",
        )
        deny_checks = {c["name"]: c for c in deny_res.get("governance_checks") or []}
        check(
            deny_checks.get(spec.check_name, {}).get("passed") is False,
            f"governed/deny did not record a failing {spec.check_name} check",
        )
        if spec.deny_detail_phrase is not None:
            check(
                spec.deny_detail_phrase
                in deny_checks.get(spec.check_name, {}).get("detail", ""),
                f"governed/deny detail did not contain {spec.deny_detail_phrase!r}",
            )
        check(
            deny_score.get("governance_failure_count") == 1,
            "governed/deny did not record exactly one governance failure",
        )
        chain = deny_res.get("tao_truth_chain") or {}
        check(
            chain.get("subject_id") == f"case::{spec.case_id}",
            "governed/deny did not surface the Tao truth chain",
        )

        # Quantify the governed-vs-ungoverned behavior from the three scored runs,
        # reusing report.build_governance_comparison so this slice is measured
        # exactly as a full benchmark run would surface it. No new schema or
        # scoring path: the comparison reads the existing optional governance
        # fields and is skipped entirely when they are absent.
        comparison = report.build_governance_comparison(
            [ungov_score, admit_score, deny_score]
        )
        check(comparison is not None, "no governance comparison was produced")
        check(
            comparison["matched_case_count"] == 1,
            "slice did not match the same case across governed and ungoverned",
        )
        governed_metrics = comparison["governed"]
        ungoverned_metrics = comparison["ungoverned"]
        check(
            ungoverned_metrics["case_count"] == 1
            and governed_metrics["case_count"] == 2,
            "slice did not partition into one ungoverned and two governed runs",
        )
        # The measurable governed-vs-ungoverned delta: governance surfaces exactly
        # the one denial (the deny scenario) the ungoverned baseline silently
        # allowed.
        check(
            ungoverned_metrics["governance_failure_count"] == 0,
            "ungoverned baseline unexpectedly recorded a governance failure",
        )
        check(
            governed_metrics["governance_failure_count"] == 1
            and governed_metrics["cases_with_governance_failure"] == 1,
            "governed runs did not record exactly the one governance failure",
        )
        deltas = comparison["deltas"]
        check(
            deltas["governance_failure_count"] == 1,
            "governed-minus-ungoverned governance failure delta was not quantified as +1",
        )

    print(
        f"{spec.smoke_name}: ok "
        f"({spec.summary_clause}; governed-minus-ungoverned "
        f"{spec.delta_label} governance-failure delta "
        f"{deltas['governance_failure_count']:+d} over "
        f"{comparison['matched_case_count']} matched case)"
    )
    return 0
