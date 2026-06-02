from __future__ import annotations

import subprocess
import time


def run_command(argv: list[str], timeout_seconds: float | None = None) -> dict:
    started = time.monotonic()
    completed = subprocess.run(argv, text=True, capture_output=True)
    return {
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "exit_code": completed.returncode,
        "timed_out": False,
        "duration_ms": int((time.monotonic() - started) * 1000),
    }
