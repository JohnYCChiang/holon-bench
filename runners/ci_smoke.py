#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile

from common import bench_root


def run(command: list[str], root: pathlib.Path) -> None:
    completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )


def main() -> int:
    root = bench_root(sys.argv[1] if len(sys.argv) > 1 else ".")
    with tempfile.TemporaryDirectory(prefix="holon-bench-ci-") as temp:
        temp_root = pathlib.Path(temp)
        artifact = temp_root / "artifact.txt"
        result = temp_root / "result.json"
        score = temp_root / "score.json"
        source = (
            root / "fixtures/python/tool_error_enum/src/tool_errors/runner.py"
        ).read_text(encoding="utf-8")
        marker = "# CI smoke marker: a harmless owned-file change exercises artifact application.\n"
        if marker in source:
            raise RuntimeError("CI smoke marker unexpectedly exists in fixture source")
        changed_source = source.replace("def run_tool", f"{marker}def run_tool", 1)
        artifact.write_text(
            f"--- FILE: src/tool_errors/runner.py ---\n{changed_source}",
            encoding="utf-8",
        )

        run(
            [
                sys.executable,
                str(root / "runners" / "run_case.py"),
                "py-tool-001",
                "--model",
                "ci-smoke",
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
        )

        result_data = json.loads(result.read_text(encoding="utf-8"))
        score_data = json.loads(score.read_text(encoding="utf-8"))
        if not all(result_data["hard_gates"].values()):
            raise RuntimeError(f"smoke result did not pass: {result_data['hard_gates']}")
        if not score_data["hard_pass"]:
            raise RuntimeError("smoke score did not record hard_pass")

    print("ci_smoke: ok (artifact -> verifier -> result -> score)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
