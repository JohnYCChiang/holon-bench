#!/usr/bin/env python3
"""Offline smoke for the Holon (`holon-cli`) driver.

Runs a single benchmark case end-to-end through the Holon driver
(generation -> verifier -> result -> score) without any remote API, model
endpoint, or compiled Holon binary. The real Holon binary is replaced by
``holon_stub.py`` (see ``HOLON_BIN``), which edits an owned file and emits
Holon governance metadata. This proves the exit criterion "a single benchmark
case can run through holon" in CI.

The direct (non-Holon) path is exercised separately by ``ci_smoke.py`` and is
left untouched here.
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
MARKER = "# holon smoke marker: harmless owned-file change via offline stub.\n"


def run(command: list[str], root: pathlib.Path, env: dict[str, str]) -> None:
    completed = subprocess.run(
        command, cwd=root, text=True, capture_output=True, check=False, env=env
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )


def main() -> int:
    root = bench_root(sys.argv[1] if len(sys.argv) > 1 else ".")
    stub = root / "runners" / "holon_stub.py"
    if not stub.is_file():
        raise RuntimeError(f"holon stub missing: {stub}")

    with tempfile.TemporaryDirectory(prefix="holon-bench-holon-smoke-") as temp:
        temp_root = pathlib.Path(temp)
        artifact = temp_root / "artifact.txt"
        result = temp_root / "result.json"
        score = temp_root / "score.json"

        # An executable shim so the driver can exec the stub as the holon binary
        # regardless of the committed file's mode or shebang interpreter.
        shim = temp_root / "holon"
        shim.write_text(
            f'#!/bin/sh\nexec "{sys.executable}" "{stub}" "$@"\n', encoding="utf-8"
        )
        shim.chmod(0o755)

        env = os.environ.copy()
        env["HOLON_BIN"] = str(shim)
        env["HOLON_STUB_TARGET"] = TARGET
        env["HOLON_STUB_ANCHOR"] = "def run_tool"
        env["HOLON_STUB_MARKER"] = MARKER
        env["HOLON_STUB_GOVERNANCE"] = "1"
        env["HOLON_STUB_CASE"] = CASE_ID

        run(
            [
                sys.executable,
                str(root / "runners" / "run_model_case.py"),
                CASE_ID,
                "--model",
                "holon-smoke",
                "--driver",
                "holon-cli",
                "--protocol",
                "artifact",
                # Never contacted: the stub edits the workspace, so the driver
                # returns before any direct-endpoint fallback.
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
                "holon-smoke",
                "--artifact-file",
                str(artifact),
                "--bench-root",
                str(root),
                "--work-root",
                str(temp_root / "work"),
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

        result_data = json.loads(result.read_text(encoding="utf-8"))
        score_data = json.loads(score.read_text(encoding="utf-8"))
        if not all(result_data["hard_gates"].values()):
            raise RuntimeError(f"smoke result did not pass: {result_data['hard_gates']}")
        if not score_data["hard_pass"]:
            raise RuntimeError("smoke score did not record hard_pass")
        if result_data.get("generation_path") != "holon_workflow":
            raise RuntimeError(
                f"unexpected generation_path: {result_data.get('generation_path')}"
            )
        if result_data.get("governance_mode") != "governed":
            raise RuntimeError("governance_mode was not surfaced from Holon output")
        chain = result_data.get("tao_truth_chain") or {}
        if chain.get("subject_id") != f"case::{CASE_ID}":
            raise RuntimeError("tao_truth_chain was not surfaced from Holon output")

    print("holon_smoke: ok (holon-cli -> verifier -> result -> score, no remote APIs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
