#!/usr/bin/env python3
"""Offline governance capability matrix over the Tao-backed witness smokes (M14).

This runner is **evidence aggregation, not a new capability class**. Each of the
three completed governed-vs-ungoverned witness smokes already proves, end-to-end
and offline, that one Tao ``EffectOp`` gate surfaces exactly the one governance
failure the ungoverned baseline silently allowed. This matrix re-drives those
existing smokes and confirms each one still reports its expected
governed-minus-ungoverned ``+1`` governance-failure delta over its one matched
case, then emits a compact matrix (human summary plus optional ``--json``).

Matrix rows (one per protected capability class):

- ``fs-write``        protects filesystem mutation
                      (``holon_fs_governance_smoke.py``).
- ``fs-read``         protects context exposure / information boundary
                      (``holon_fs_read_governance_smoke.py``).
- ``process-control`` protects liveness/ownership of running processes
                      (``holon_process_governance_smoke.py``).

The matrix **fails closed**: a row is confirmed only when its smoke exits cleanly,
reports ``ok``, and surfaces exactly the expected governance-failure delta over
the expected matched-case count. Any nonzero exit, timeout, unparseable summary,
or unexpected delta/matched-case count marks the row (and the matrix) failed and
the process exits nonzero.

Safety: this aggregator only re-invokes the existing offline smokes via
``sys.executable``. It runs no live process-control command (no ``kill`` /
``pkill`` / ``killall`` / ``pgrep`` / ``ps`` / ``systemctl`` / ``jobs``) and
never inspects, attaches to, or interferes with any running service. The
process-control row stays stub-only, exactly as its smoke is.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
from typing import Any, Callable

from common import bench_root

# Each row names a protected capability class, the existing offline smoke that
# proves it, and the governance evidence the smoke must surface. The expected
# delta/matched-case values mirror the per-smoke checks; confirming them here is
# what lets the matrix fail closed if a smoke silently stops measuring the gate.
ROWS: list[dict[str, Any]] = [
    {
        "capability": "fs-write",
        "domain_claim": "protects filesystem mutation",
        "runner": "holon_fs_governance_smoke.py",
        "expected_delta": 1,
        "expected_matched_cases": 1,
    },
    {
        "capability": "fs-read",
        "domain_claim": "protects context exposure / information boundary",
        "runner": "holon_fs_read_governance_smoke.py",
        "expected_delta": 1,
        "expected_matched_cases": 1,
    },
    {
        "capability": "process-control",
        "domain_claim": "protects liveness/ownership of running processes",
        "runner": "holon_process_governance_smoke.py",
        "expected_delta": 1,
        "expected_matched_cases": 1,
    },
]

# Stable contract tag for the JSON matrix artifact. Machine consumers should
# reject any document whose schema_version they do not recognize. Bump only on a
# breaking shape change; the JSON Schema lives at
# ``schemas/governance_matrix.schema.json``.
SCHEMA_VERSION = "governance-matrix/v1"

# Matches the shared suffix every smoke prints, e.g.
# "... governance-failure delta +1 over 1 matched case)".
SUMMARY_RE = re.compile(r"delta\s+([+-]?\d+)\s+over\s+(\d+)\s+matched case")

# Generous per-smoke ceiling so a hung smoke fails the matrix closed instead of
# blocking forever. Each smoke is a short offline pipeline well under this.
SMOKE_TIMEOUT_SECONDS = 600


def run_smoke(root: pathlib.Path, runner_name: str) -> subprocess.CompletedProcess:
    """Invoke one existing smoke offline via ``sys.executable`` and capture output."""
    runner_path = root / "runners" / runner_name
    command = [sys.executable, str(runner_path), str(root)]
    try:
        return subprocess.run(
            command,
            cwd=str(root),
            text=True,
            capture_output=True,
            check=False,
            timeout=SMOKE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as err:
        # Fail closed: surface as a non-clean exit with a clear marker.
        return subprocess.CompletedProcess(
            command,
            returncode=None,
            stdout=err.stdout or "",
            stderr=(err.stderr or "") + f"\nTIMEOUT after {SMOKE_TIMEOUT_SECONDS}s",
        )


def _summary_line(stdout: str, smoke_name: str) -> str:
    """The last stdout line naming this smoke (its human result line)."""
    for line in reversed(stdout.splitlines()):
        if smoke_name in line and line.strip():
            return line.strip()
    return ""


def evaluate_row(
    root: pathlib.Path,
    row: dict[str, Any],
    runner: Callable[[pathlib.Path, str], subprocess.CompletedProcess] = run_smoke,
) -> dict[str, Any]:
    """Run one row's smoke and confirm its expected governance evidence."""
    smoke_name = pathlib.Path(row["runner"]).stem
    completed = runner(root, row["runner"])
    stdout = completed.stdout or ""
    stderr = completed.stderr or ""

    failures: list[str] = []
    if completed.returncode != 0:
        failures.append(f"runner exited non-clean (returncode={completed.returncode})")
    if f"{smoke_name}: ok" not in stdout:
        failures.append("runner did not report ok")

    observed_delta: int | None = None
    observed_matched_cases: int | None = None
    match = SUMMARY_RE.search(stdout)
    if match is None:
        failures.append("could not parse governance-failure delta / matched-case count")
    else:
        observed_delta = int(match.group(1))
        observed_matched_cases = int(match.group(2))
        if observed_delta != row["expected_delta"]:
            failures.append(
                f"governance-failure delta {observed_delta:+d} "
                f"!= expected {row['expected_delta']:+d}"
            )
        if observed_matched_cases != row["expected_matched_cases"]:
            failures.append(
                f"matched-case count {observed_matched_cases} "
                f"!= expected {row['expected_matched_cases']}"
            )

    result: dict[str, Any] = {
        "capability": row["capability"],
        "domain_claim": row["domain_claim"],
        "runner": f"runners/{row['runner']}",
        "expected_delta": row["expected_delta"],
        "expected_matched_cases": row["expected_matched_cases"],
        "exit_code": completed.returncode,
        "observed_delta": observed_delta,
        "observed_matched_cases": observed_matched_cases,
        "summary_line": _summary_line(stdout, smoke_name),
        "ok": not failures,
        "failures": failures,
    }
    if failures:
        # Only attach diagnostics on failure, truncated to stay compact.
        result["stdout_tail"] = stdout[-2000:]
        result["stderr_tail"] = stderr[-2000:]
    return result


def build_matrix(
    root: pathlib.Path,
    rows: list[dict[str, Any]] = ROWS,
    runner: Callable[[pathlib.Path, str], subprocess.CompletedProcess] = run_smoke,
) -> dict[str, Any]:
    """Drive every row and aggregate into a fail-closed matrix."""
    row_results = [evaluate_row(root, row, runner) for row in rows]
    return {
        "schema_version": SCHEMA_VERSION,
        "matrix": "holon_governance_matrix",
        "ok": all(item["ok"] for item in row_results),
        "row_count": len(row_results),
        "rows": row_results,
    }


def render_human(matrix: dict[str, Any]) -> str:
    lines = ["holon_governance_matrix:"]
    width = max((len(item["capability"]) for item in matrix["rows"]), default=0)
    for item in matrix["rows"]:
        status = "PASS" if item["ok"] else "FAIL"
        delta = item["observed_delta"]
        matched = item["observed_matched_cases"]
        evidence = (
            f"delta {delta:+d} over {matched} matched case"
            if delta is not None and matched is not None
            else "no governance evidence parsed"
        )
        lines.append(
            f"  {item['capability']:<{width}}  {status}  "
            f"{evidence}  ({item['domain_claim']})"
        )
        if not item["ok"]:
            for failure in item["failures"]:
                lines.append(f"      - {failure}")
    confirmed = sum(1 for item in matrix["rows"] if item["ok"])
    verdict = "ok" if matrix["ok"] else "FAILED (fail-closed)"
    lines.append(
        f"  {verdict}: {confirmed}/{matrix['row_count']} capability rows confirmed "
        "(offline, no remote APIs, no live process touched)"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="path inside the benchmark root (default: current directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the matrix as JSON to stdout instead of the human summary",
    )
    parser.add_argument(
        "--out",
        metavar="PATH",
        help=(
            "write the JSON matrix artifact to PATH (parent dirs created); "
            "stdout still shows the human summary unless --json is also given"
        ),
    )
    args = parser.parse_args(argv)

    root = bench_root(args.root)
    matrix = build_matrix(root)

    # One canonical encoding shared by stdout (--json) and the artifact (--out)
    # so a file written and a value printed are byte-for-byte the same.
    encoded = json.dumps(matrix, indent=2, sort_keys=True)

    if args.out:
        out_path = pathlib.Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(encoded + "\n", encoding="utf-8")

    if args.json:
        print(encoded)
    else:
        print(render_human(matrix))
    # Exit code follows the fail-closed matrix verdict regardless of output mode.
    return 0 if matrix["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
