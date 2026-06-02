from __future__ import annotations

import subprocess
import time


def run_command(argv: list[str], timeout_seconds: float | None = None) -> dict:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            argv,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
        )
        return {
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "exit_code": completed.returncode,
            "timed_out": False,
            "duration_ms": int((time.monotonic() - started) * 1000),
        }
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if exc.stdout is not None else b""
        stderr = exc.stderr if exc.stderr is not None else b""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return {
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": -1,
            "timed_out": True,
            "duration_ms": int((time.monotonic() - started) * 1000),
        }
