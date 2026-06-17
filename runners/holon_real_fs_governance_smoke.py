#!/usr/bin/env python3
"""Real-binary smoke for the Tao fs EffectOp witness gate (holon#7 / 394a734).

Holon#7 (merged in ``taichi/holon`` PR #8, merge commit ``394a734``) added the
external config surface for the fs permission gate (holon#5 / tao#5): the runtime
installs a ``TaoEffectOpWitnessSource`` from an on-disk witness file pointed at by
``HOLON_TAO_FS_WITNESS=<path>`` (or the ``tao.fsWitness.path`` settings key; the
env wins). This smoke drives the *real* Holon binary through the same three
configurations the offline stub smoke covers, but using the real config surface
and real witness files instead of an in-process model:

- unconfigured   ``HOLON_TAO_FS_WITNESS`` unset -> legacy ungated path: fs write
  happens; no governance failure surfaces.
- governed/admit a witness file grants the fs EffectOp (``decision: admit`` with
  a ``resultType``) -> fs write happens; passing ``fs_permission`` check.
- governed/deny  a witness file with no matching grant (missing grant) -> fs
  write blocked; failing ``fs_permission`` check; one governance failure.

CI / no-binary behavior
-----------------------
The compiled Holon binary is not available in default CI and would require a live
model endpoint, so this smoke is **opt-in**. When no real binary is found at
``HOLON_BIN`` (or the default path), it prints a clear ``not-run`` status and
exits 0, leaving default CI unaffected. The offline, binary-free coverage lives
in ``holon_fs_governance_smoke.py`` and is preserved unchanged.

Running it
----------
- Against the real binary::

      HOLON_BIN=/path/to/holon \
      HOLON_SMOKE_ENDPOINT=http://127.0.0.1:8086/v1 \
      python3 runners/holon_real_fs_governance_smoke.py .

  A live OpenAI-compatible endpoint is required so the agent actually attempts
  the fs write the witness then gates.

- Offline rehearsal of the witness contract (no real binary, no endpoint): point
  ``HOLON_BIN`` at the offline stub shim, which honors ``HOLON_TAO_FS_WITNESS``
  by reading the same witness files. This is what the unit tests do; see
  ``runners/test_holon_real_fs_governance.py`` and
  ``.claude/tasks/holon-tao-witness-config-surface.md``.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import tempfile

from common import bench_root
import holon_witness

CASE_ID = "py-tool-001"
TARGET = "src/tool_errors/runner.py"
ANCHOR = "def run_tool"
MARKER = "# holon real fs-witness smoke marker: gated owned-file change.\n"
EFFECT_OP = "fs.edit"

DEFAULT_HOLON_BIN = "/home/taichi/Migration/holon/target/debug/holon"
DEFAULT_ENDPOINT = "http://127.0.0.1:1/v1"


def resolve_binary() -> pathlib.Path | None:
    """Return the real Holon binary path if present and executable, else None."""
    holon_bin = pathlib.Path(os.environ.get("HOLON_BIN", DEFAULT_HOLON_BIN))
    if holon_bin.is_file() and os.access(holon_bin, os.X_OK):
        return holon_bin
    return None


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
    holon_bin: pathlib.Path,
    endpoint: str,
    temp_root: pathlib.Path,
    label: str,
    witness_path: pathlib.Path | None,
) -> tuple[str, dict, dict]:
    artifact = temp_root / f"{label}_artifact.txt"
    result = temp_root / f"{label}_result.json"
    score = temp_root / f"{label}_score.json"

    env = os.environ.copy()
    env["HOLON_BIN"] = str(holon_bin)
    env["HOLON_STUB_TARGET"] = TARGET
    env["HOLON_STUB_ANCHOR"] = ANCHOR
    env["HOLON_STUB_MARKER"] = MARKER
    env["HOLON_STUB_CASE"] = CASE_ID
    env["HOLON_STUB_FS_EFFECT_OP"] = EFFECT_OP
    # The real config surface: env points at the on-disk witness file. Unset
    # means legacy ungated. Never lean on the in-process HOLON_STUB_FS_WITNESS
    # model here -- this smoke exercises the real witness file path only.
    env.pop("HOLON_STUB_FS_WITNESS", None)
    if witness_path is not None:
        env["HOLON_TAO_FS_WITNESS"] = str(witness_path)
    else:
        env.pop("HOLON_TAO_FS_WITNESS", None)

    model = f"holon-real-fs-{label}"
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
            "--endpoint",
            endpoint,
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
        raise RuntimeError(f"holon_real_fs_governance_smoke: {message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bench_root", nargs="?", default=".")
    parser.add_argument(
        "--endpoint",
        default=os.environ.get("HOLON_SMOKE_ENDPOINT", DEFAULT_ENDPOINT),
        help="OpenAI-compatible endpoint for the real binary (live model needed).",
    )
    args = parser.parse_args()

    root = bench_root(args.bench_root)
    holon_bin = resolve_binary()
    if holon_bin is None:
        target = os.environ.get("HOLON_BIN", DEFAULT_HOLON_BIN)
        print(
            "holon_real_fs_governance_smoke: not-run "
            f"(no executable Holon binary at {target}; set HOLON_BIN to enable). "
            "Offline coverage: runners/holon_fs_governance_smoke.py."
        )
        return 0

    with tempfile.TemporaryDirectory(prefix="holon-bench-real-fs-smoke-") as temp:
        temp_root = pathlib.Path(temp)

        # unconfigured / legacy ungated: no witness file -> baseline allow.
        ungov_art, ungov_res, ungov_score = run_scenario(
            root, holon_bin, args.endpoint, temp_root, "unconfigured", witness_path=None
        )
        check(
            MARKER.strip() in ungov_art,
            "unconfigured did not preserve baseline allow (legacy ungated)",
        )
        check(
            ungov_res.get("governance_mode") != "governed",
            "unconfigured run was unexpectedly governed",
        )
        check(
            ungov_score.get("governance_failure_count") == 0,
            "unconfigured run unexpectedly recorded a governance failure",
        )

        # governed/admit: witness grants the fs EffectOp.
        admit_witness = holon_witness.write_witness(
            temp_root / "admit_witness.json",
            [holon_witness.admit_grant(EFFECT_OP, TARGET, result_type="Patch")],
        )
        admit_art, admit_res, admit_score = run_scenario(
            root, holon_bin, args.endpoint, temp_root, "admit", witness_path=admit_witness
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

        # governed/deny: witness with no matching grant -> missing-grant deny.
        # A well-formed file whose only grant targets a different EffectOp, so the
        # fs.edit op has no matching row and fails closed.
        deny_witness = holon_witness.write_witness(
            temp_root / "deny_witness.json",
            [holon_witness.admit_grant("fs.delete", TARGET, result_type="Unit")],
        )
        deny_art, deny_res, deny_score = run_scenario(
            root, holon_bin, args.endpoint, temp_root, "deny", witness_path=deny_witness
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
        "holon_real_fs_governance_smoke: ok "
        "(real binary via HOLON_TAO_FS_WITNESS: unconfigured allow vs "
        "governed admit/deny)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
