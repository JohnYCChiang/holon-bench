#!/usr/bin/env python3
"""Offline governed-vs-ungoverned smoke for the Holon network-egress gate (M19).

The network-egress sibling of ``holon_process_governance_smoke.py``. Where that
smoke gates a modeled process-control action, this one gates a *modeled*
network-egress action. Tao/Holon landed the network-egress EffectOps
``net.resolve | net.connect | net.send`` (tao#22) and Holon gates selected
outbound commands narrow-only. The domain claim is the *external-contact /
exfiltration boundary* (which external endpoints a context may reach and what it
may send outward), not filesystem write/read exposure or process liveness.

The gated action here is **modeled only** and harmless: this smoke never runs
``curl`` / ``wget`` / ``nc`` / ``dig`` or any command that resolves a name, opens
a socket, or sends a byte, and it never touches ``zhenren_bridge`` or any network
service. The offline ``holon_stub`` models the witness decision under
``HOLON_STUB_NET_WITNESS`` and records the modeled action as an inert artifact
marker -- exactly the way the fs and process gates decide whether a modeled action
is applied. All three configurations are driven through the *real* Holon driver ->
verifier -> result -> score pipeline, with no remote API, model endpoint, or
compiled Holon binary.

Scenarios (same case, same modeled action, different witness config):

- unconfigured  no witness installed -> ungoverned baseline allow: the modeled
  action is recorded; ``governance_mode == "ungoverned"``; no governance failures.
- governed/admit  witness grants the egress EffectOp: the modeled action is
  recorded; passing ``network_permission`` check.
- governed/deny   witness denies (missing grant): the modeled action is blocked
  (external-contact boundary preserved); failing ``network_permission`` check; one
  governance failure.

After driving the three runs the smoke quantifies the governed-vs-ungoverned
network-egress behavior with ``report.build_governance_comparison`` (the same
function ``report.py`` and the fs/process smokes use). The governed runs surface
exactly the one egress denial the ungoverned baseline silently allowed
(governance-failure delta ``+1`` over one matched case). The comparison reads only
the existing optional governance fields, so legacy results without them are
unaffected.
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
# An inert marker standing in for the modeled network-egress action record. It is
# never a real network command -- on a deny it is never recorded.
MARKER = "# holon network-witness smoke marker: modeled net.send action via stub.\n"
NET_OP = "net.send"


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
    env["HOLON_STUB_NET_OP"] = NET_OP
    if witness is not None:
        env["HOLON_STUB_NET_WITNESS"] = witness
    else:
        env.pop("HOLON_STUB_NET_WITNESS", None)

    model = f"holon-network-{label}"
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
            # Never contacted: admit records the modeled action in the workspace,
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
        raise RuntimeError(f"holon_network_governance_smoke: {message}")


def main() -> int:
    root = bench_root(sys.argv[1] if len(sys.argv) > 1 else ".")
    stub = root / "runners" / "holon_stub.py"
    if not stub.is_file():
        raise RuntimeError(f"holon stub missing: {stub}")

    with tempfile.TemporaryDirectory(prefix="holon-bench-network-smoke-") as temp:
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
        check(
            MARKER.strip() in ungov_art,
            "ungoverned did not preserve baseline allow (modeled action not recorded)",
        )
        check(
            ungov_res.get("governance_mode") == "ungoverned",
            "ungoverned run was not labeled ungoverned in the result",
        )
        check(
            ungov_score.get("governance_failure_count") == 0,
            "ungoverned run unexpectedly recorded a governance failure",
        )

        # Governed + admit: witness grants the egress EffectOp.
        admit_art, admit_res, admit_score = run_scenario(
            root, shim, temp_root, "admit", witness="admit"
        )
        check(
            MARKER.strip() in admit_art,
            "governed/admit did not allow the modeled network egress action",
        )
        check(
            admit_res.get("governance_mode") == "governed",
            "governed/admit run was not labeled governed",
        )
        admit_checks = {c["name"]: c for c in admit_res.get("governance_checks") or []}
        check(
            admit_checks.get("network_permission", {}).get("passed") is True,
            "governed/admit did not record a passing network_permission check",
        )
        check(
            admit_score.get("governance_failure_count") == 0,
            "governed/admit unexpectedly recorded a governance failure",
        )

        # Governed + deny: witness denies (missing grant) -> action blocked.
        deny_art, deny_res, deny_score = run_scenario(
            root, shim, temp_root, "deny", witness="deny"
        )
        check(
            MARKER.strip() not in deny_art,
            "governed/deny did NOT block the modeled egress action (baseline leaked through)",
        )
        check(
            deny_res.get("governance_mode") == "governed",
            "governed/deny run was not labeled governed",
        )
        deny_checks = {c["name"]: c for c in deny_res.get("governance_checks") or []}
        check(
            deny_checks.get("network_permission", {}).get("passed") is False,
            "governed/deny did not record a failing network_permission check",
        )
        check(
            "external-contact boundary preserved"
            in deny_checks.get("network_permission", {}).get("detail", ""),
            "governed/deny did not frame the denial as preserving the external-contact boundary",
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

        # Quantify the governed-vs-ungoverned network-egress behavior from the
        # three scored runs, reusing report.build_governance_comparison so this
        # egress slice is measured exactly as a full benchmark run would surface
        # it. No new schema or scoring path: the comparison reads the existing
        # optional governance fields and is skipped entirely when they are absent.
        comparison = report.build_governance_comparison(
            [ungov_score, admit_score, deny_score]
        )
        check(comparison is not None, "no governance comparison was produced")
        check(
            comparison["matched_case_count"] == 1,
            "network slice did not match the same case across governed and ungoverned",
        )
        governed_metrics = comparison["governed"]
        ungoverned_metrics = comparison["ungoverned"]
        check(
            ungoverned_metrics["case_count"] == 1
            and governed_metrics["case_count"] == 2,
            "network slice did not partition into one ungoverned and two governed runs",
        )
        # The measurable governed-vs-ungoverned network-egress delta: governance
        # surfaces exactly the one egress denial (the deny scenario) that the
        # ungoverned baseline silently allowed.
        check(
            ungoverned_metrics["governance_failure_count"] == 0,
            "ungoverned baseline unexpectedly recorded a governance failure",
        )
        check(
            governed_metrics["governance_failure_count"] == 1
            and governed_metrics["cases_with_governance_failure"] == 1,
            "governed runs did not record exactly the one network-egress governance failure",
        )
        deltas = comparison["deltas"]
        check(
            deltas["governance_failure_count"] == 1,
            "governed-minus-ungoverned governance failure delta was not quantified as +1",
        )

    print(
        "holon_network_governance_smoke: ok "
        "(ungoverned allow vs governed admit/deny modeled network egress, no "
        f"remote APIs and no real network touched; governed-minus-ungoverned "
        f"network governance-failure delta "
        f"{deltas['governance_failure_count']:+d} over "
        f"{comparison['matched_case_count']} matched case)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
