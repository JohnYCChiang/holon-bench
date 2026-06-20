#!/usr/bin/env python3
"""Offline smoke for the Holon governed-effect acceptance record (tao#24).

Where the per-class governance smokes prove the *gate* (an admitted mutation-side
effect surfaces a governed-minus-ungoverned `+1` denial delta), this smoke proves
the *record*: an admitted mutation-side effect produces an id-only `TestResult`
acceptance record (`tao#24`), and nothing else does. The general acceptance record
says the agent performs, the runner records, and you record only what was admitted
and actually mutated world state — so:

- **governed/admit + mutation-side** (`process.kill`) → an `acceptance_record` with
  `fact_kind="TestResult"`, `authority="runner"`, the witness op id, and the frozen
  outcome type. Id-only: no pid/command/target/payload.
- **governed/deny** → **no** record (a denied effect accepts nothing).
- **unconfigured/ungoverned** → **no** record (no witness ran).
- **governed/admit + observe-only** (`fs.read`) → **no** record (a read mutates
  nothing; nothing to accept).

The action is modeled only and offline: the stub never kills a process, opens a
socket, or exposes a real file — it records an inert governance marker, exactly as
the per-class smokes do. All runs go through the real Holon driver -> verifier ->
result pipeline; the record is read from the result's `acceptance_record` field.
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
MARKER = "# holon acceptance-record smoke marker: modeled effect via stub.\n"


def run(command: list[str], root: pathlib.Path, env: dict[str, str]) -> None:
    completed = subprocess.run(
        command, cwd=root, text=True, capture_output=True, check=False, env=env
    )
    if completed.returncode not in (0, 1):
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )


def run_scenario(
    root: pathlib.Path,
    shim: pathlib.Path,
    temp_root: pathlib.Path,
    label: str,
    overrides: dict[str, str],
) -> dict:
    """Drive one scenario and return its run-case result dict."""
    artifact = temp_root / f"{label}_artifact.txt"
    result = temp_root / f"{label}_result.json"

    env = os.environ.copy()
    env["HOLON_BIN"] = str(shim)
    env["HOLON_STUB_TARGET"] = TARGET
    env["HOLON_STUB_ANCHOR"] = ANCHOR
    env["HOLON_STUB_MARKER"] = MARKER
    env["HOLON_STUB_CASE"] = CASE_ID
    # Clear any inherited witness env so each scenario is hermetic.
    for key in (
        "HOLON_STUB_PROCESS_WITNESS",
        "HOLON_STUB_NET_WITNESS",
        "HOLON_STUB_FS_WITNESS",
        "HOLON_STUB_FS_KIND",
    ):
        env.pop(key, None)
    env.update(overrides)

    model = f"holon-accept-{label}"
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
    return json.loads(result.read_text(encoding="utf-8"))


def check(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(f"holon_acceptance_record_smoke: {message}")


def main() -> int:
    root = bench_root(sys.argv[1] if len(sys.argv) > 1 else ".")
    stub = root / "runners" / "holon_stub.py"
    if not stub.is_file():
        raise RuntimeError(f"holon stub missing: {stub}")

    with tempfile.TemporaryDirectory(prefix="holon-bench-accept-smoke-") as temp:
        temp_root = pathlib.Path(temp)
        shim = temp_root / "holon"
        shim.write_text(
            f'#!/bin/sh\nexec "{sys.executable}" "{stub}" "$@"\n', encoding="utf-8"
        )
        shim.chmod(0o755)

        # 1) governed/admit + mutation-side (process.kill) -> a TestResult record.
        admit = run_scenario(
            root,
            shim,
            temp_root,
            "kill-admit",
            {"HOLON_STUB_PROCESS_WITNESS": "admit", "HOLON_STUB_PROCESS_OP": "process.kill"},
        )
        record = admit.get("acceptance_record")
        check(
            isinstance(record, dict),
            "governed/admit mutation-side effect produced no acceptance record",
        )
        check(
            record.get("fact_kind") == "TestResult",
            "acceptance record fact_kind is not TestResult (no new FactKind)",
        )
        check(
            record.get("authority") == "runner",
            "acceptance record authority is not runner (must never be an agent)",
        )
        check(
            record.get("subject") == f"case::{CASE_ID}",
            "acceptance record subject is not the canonical case id",
        )
        check(
            record.get("witness_op") == "process.kill",
            "acceptance record witness_op is not the admitted process.kill op",
        )
        check(
            record.get("outcome_type") == "Killed",
            "acceptance record outcome_type is not the frozen Killed outcome",
        )
        # Id-only: no runtime value (target path, marker, pid, command) leaked in.
        blob = json.dumps(record)
        for leak in [TARGET, MARKER.strip(), "kill ", "4242"]:
            check(
                leak not in blob,
                f"acceptance record must stay id-only (leaked {leak!r})",
            )

        # 2) governed/deny -> no record (a denied effect accepts nothing).
        deny = run_scenario(
            root,
            shim,
            temp_root,
            "kill-deny",
            {"HOLON_STUB_PROCESS_WITNESS": "deny", "HOLON_STUB_PROCESS_OP": "process.kill"},
        )
        check(
            deny.get("acceptance_record") is None,
            "governed/deny produced an acceptance record (a denied effect accepts nothing)",
        )

        # 3) unconfigured/ungoverned -> no record (no witness ran).
        ungov = run_scenario(
            root,
            shim,
            temp_root,
            "kill-ungoverned",
            {"HOLON_STUB_PROCESS_WITNESS": "none", "HOLON_STUB_PROCESS_OP": "process.kill"},
        )
        check(
            ungov.get("acceptance_record") is None,
            "ungoverned baseline produced an acceptance record (no witness ran)",
        )

        # 4) governed/admit + observe-only (fs.read) -> no record (nothing to accept).
        read_admit = run_scenario(
            root,
            shim,
            temp_root,
            "read-admit",
            {"HOLON_STUB_FS_WITNESS": "admit", "HOLON_STUB_FS_KIND": "read"},
        )
        check(
            read_admit.get("governance_mode") == "governed",
            "fs-read admit scenario was not governed (harness check)",
        )
        check(
            read_admit.get("acceptance_record") is None,
            "an observe-only fs read produced an acceptance record (nothing to accept)",
        )

    print(
        "holon_acceptance_record_smoke: ok "
        "(admitted mutation-side process.kill recorded as an id-only TestResult "
        "acceptance record; deny / ungoverned / observe-only read record nothing, "
        "no remote APIs and no real process/file touched)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
