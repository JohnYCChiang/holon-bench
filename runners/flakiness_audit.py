#!/usr/bin/env python3
"""Flakiness audit for case verifiers.

Timing-based and concurrency tests can flip pass/fail on a CI scheduling glitch.
This tool has two modes:

  --scan (default): a CPU-light STATIC scan. Greps each case's fixture (hidden +
    visible test files) and verifier command strings for risk patterns — tight
    ``time.After`` / ``time.Sleep`` windows, ``runtime.NumGoroutine`` leak checks,
    unseeded randomness, and concurrency fixtures whose verifier omits ``-race`` —
    and writes reports/flakiness.json with a flagged list.

  --verify N: HEAVY. For each flagged case that has a reference solution under
    solutions/, re-run its hidden+mutation verifiers N times on the solution and
    flag any run-to-run nondeterminism. (Run this off the critical path.)
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

from common import bench_root, load_cases

TIGHT_AFTER_MS = 100  # time.After windows at/below this are flake-prone

PATTERNS = {
    "go_time_after": re.compile(r"time\.After\((\d+)\s*\*\s*time\.Millisecond\)"),
    "go_sleep": re.compile(r"time\.Sleep\("),
    "go_numgoroutine": re.compile(r"runtime\.NumGoroutine"),
    "py_sleep": re.compile(r"time\.sleep\("),
    "py_unseeded_random": re.compile(r"\brandom\.(random|randint|choice|shuffle)\("),
    "rust_sleep": re.compile(r"thread::sleep|std::thread::sleep"),
    "wall_clock": re.compile(r"Instant::now\(|time\.Now\(\)|datetime\.now\("),
}


def _fixture_text(root: pathlib.Path, fixture: str) -> list[tuple[str, str]]:
    base = root / fixture
    files = []
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        if any(part in {"target", "__pycache__", ".dart_tool", "build", ".git"} for part in path.parts):
            continue
        if path.suffix in {".go", ".py", ".rs", ".dart"}:
            try:
                files.append((str(path.relative_to(base)), path.read_text(encoding="utf-8", errors="ignore")))
            except OSError:
                pass
    return files


def scan(root: pathlib.Path, cases: list[dict]) -> list[dict]:
    flagged = []
    for case in cases:
        verifier = case.get("verifier", {})
        commands = " ".join(
            (verifier.get("commands") or [])
            + (verifier.get("hidden_commands") or [])
            + (verifier.get("mutation_commands") or [])
        )
        reasons = []
        has_concurrency = False
        for rel, text in _fixture_text(root, case["fixture"]):
            for name, pattern in PATTERNS.items():
                for match in pattern.finditer(text):
                    if name == "go_time_after":
                        ms = int(match.group(1))
                        if ms <= TIGHT_AFTER_MS:
                            reasons.append(f"tight time.After({ms}ms) in {rel}")
                        has_concurrency = True
                    elif name == "go_numgoroutine":
                        reasons.append(f"NumGoroutine leak check in {rel}")
                        has_concurrency = True
                    elif name in {"go_sleep", "py_sleep", "rust_sleep"}:
                        reasons.append(f"{name} in {rel}")
                    elif name == "py_unseeded_random":
                        reasons.append(f"unseeded random in {rel}")
                    elif name == "wall_clock":
                        reasons.append(f"wall-clock dependency in {rel}")
                    break  # one hit per pattern per file is enough
        # concurrency fixture whose verifier omits -race
        if has_concurrency and "go test" in commands and "-race" not in commands:
            reasons.append("concurrency test without -race")
        if reasons:
            flagged.append({
                "case_id": case["id"],
                "track": case["track"],
                "language": case.get("language"),
                "reasons": sorted(set(reasons)),
            })
    return flagged


def verify(root: pathlib.Path, flagged: list[dict], repeats: int) -> list[dict]:
    solutions = root / "solutions"
    results = []
    with tempfile.TemporaryDirectory(prefix="flake-") as temp:
        tmp = pathlib.Path(temp)
        cases = {c["id"]: c for c in load_cases(root)}
        for entry in flagged:
            cid = entry["case_id"]
            case = cases[cid]
            verifier = case.get("verifier", {})
            cmds = (verifier.get("hidden_commands") or []) + (verifier.get("mutation_commands") or [])
            if not cmds or not (solutions / f"{cid}.txt").exists():
                continue
            ws = tmp / cid
            shutil.copytree(root / case["fixture"], ws)
            # apply the reference solution (the --- FILE: --- artifact) into the workspace
            sol_text = (solutions / f"{cid}.txt").read_text(encoding="utf-8")
            parts = re.split(r"--- FILE: (.*?) ---\n", sol_text)
            for rel, content in zip(parts[1::2], parts[2::2]):
                target = ws / rel.strip()
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            timeout = int(verifier.get("timeout_seconds", 120))
            outcomes = []
            for _ in range(repeats):
                ok = all(subprocess.run(c, shell=True, cwd=ws, capture_output=True, text=True, timeout=timeout).returncode == 0 for c in cmds)
                outcomes.append(ok)
            shutil.rmtree(ws, ignore_errors=True)
            if len(set(outcomes)) > 1:
                results.append({"case_id": cid, "outcomes": outcomes, "flaky": True})
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bench_root", nargs="?", default=".")
    parser.add_argument("--verify", type=int, default=0, help="re-run flagged cases N times to confirm flakiness (heavy)")
    parser.add_argument("--out", default="reports/flakiness.json")
    args = parser.parse_args()

    root = bench_root(args.bench_root)
    cases = load_cases(root)
    flagged = scan(root, cases)

    report = {"scanned": len(cases), "flagged": len(flagged), "cases": flagged}
    if args.verify:
        report["verify"] = verify(root, flagged, args.verify)

    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    by_track: dict[str, int] = {}
    for entry in flagged:
        by_track[entry["track"]] = by_track.get(entry["track"], 0) + 1
    print(f"flakiness_audit: {len(flagged)}/{len(cases)} cases flagged", file=sys.stderr)
    for track, count in sorted(by_track.items()):
        print(f"  {track}: {count}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
