#!/usr/bin/env python3
"""Golden-solve oracle.

Certifies that every case is genuinely solvable and that its verifiers actually
gate, using a committed reference solution per case stored under ``solutions/``.

For each case ``<id>`` with a ``solutions/<id>.txt`` artifact (the existing
``--- FILE: <path> ---`` format the model protocol already uses):

  1. SOLVABILITY — apply the reference solution via ``run_case.py`` and require
     every hard gate to pass (patch applies, compiles, visible+hidden+mutation
     tests pass, scope/safety/semantic gates pass). This proves the case is
     solvable AND that no verifier is broken in the failing direction.

  2. GATING (``--gating``) — materialize the broken ship-state fixture and run
     the hidden + mutation commands against it; at least one must FAIL. This
     proves the verifier is not vacuous (always-passing). Reference fixtures that
     legitimately ship green are reported, not failed.

Emits ``reports/oracle.json``. Exits non-zero if any case with a solution fails
solvability, or (without ``--allow-missing``) if any case lacks a solution.

This is a permanent regression guard: if a future edit breaks a case or weakens
a verifier, the oracle fails.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

from common import bench_root, load_cases


def _run_case(root: pathlib.Path, case_id: str, solution: pathlib.Path, work: pathlib.Path, out: pathlib.Path) -> dict | None:
    proc = subprocess.run(
        [
            sys.executable,
            str(root / "runners" / "run_case.py"),
            case_id,
            "--model",
            "oracle",
            "--artifact-file",
            str(solution),
            "--bench-root",
            str(root),
            "--work-root",
            str(work),
            "--out",
            str(out),
        ],
        capture_output=True,
        text=True,
    )
    if not out.exists():
        return {"_error": proc.stderr.strip()[-800:] or proc.stdout.strip()[-800:]}
    return json.loads(out.read_text(encoding="utf-8"))


def _gating_check(root: pathlib.Path, case: dict, scratch: pathlib.Path) -> dict | None:
    """Run hidden+mutation commands against the broken ship-state fixture.

    Returns {"hidden_pass", "mutation_pass", "gates"} or None if the case has no
    hidden/mutation commands. ``gates`` is True iff at least one tier fails on the
    broken state (i.e. the verifier is not vacuous).
    """
    verifier = case.get("verifier", {})
    hidden = verifier.get("hidden_commands") or []
    mutation = verifier.get("mutation_commands") or []
    if not hidden and not mutation:
        return None
    timeout = int(verifier.get("timeout_seconds", 120))
    workspace = scratch / case["id"]
    if workspace.exists():
        shutil.rmtree(workspace)
    shutil.copytree(root / case["fixture"], workspace)

    def all_pass(commands: list[str]) -> bool:
        for command in commands:
            proc = subprocess.run(command, shell=True, cwd=workspace, capture_output=True, text=True, timeout=timeout)
            if proc.returncode != 0:
                return False
        return True

    hidden_pass = all_pass(hidden) if hidden else True
    mutation_pass = all_pass(mutation) if mutation else True
    shutil.rmtree(workspace, ignore_errors=True)
    return {
        "hidden_pass": hidden_pass,
        "mutation_pass": mutation_pass,
        "gates": (not hidden_pass) or (not mutation_pass),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bench_root", nargs="?", default=".")
    parser.add_argument("--track", help="only certify cases in this track")
    parser.add_argument("--case", help="only certify this single case id")
    parser.add_argument("--gating", action="store_true", help="also verify verifiers gate on the broken ship-state")
    parser.add_argument("--allow-missing", action="store_true", help="do not fail on cases that lack a reference solution")
    parser.add_argument("--out", default="reports/oracle.json")
    args = parser.parse_args()

    root = bench_root(args.bench_root)
    cases = load_cases(root)
    if args.track:
        cases = [c for c in cases if c.get("track") == args.track]
    if args.case:
        cases = [c for c in cases if c.get("id") == args.case]
    solutions = root / "solutions"

    rows: list[dict] = []
    missing: list[str] = []
    unsolved: list[str] = []
    vacuous: list[str] = []

    with tempfile.TemporaryDirectory(prefix="oracle-") as temp:
        tmp = pathlib.Path(temp)
        for case in cases:
            cid = case["id"]
            sol = solutions / f"{cid}.txt"
            if not sol.exists():
                missing.append(cid)
                rows.append({"case_id": cid, "track": case.get("track"), "status": "MISSING_SOLUTION"})
                continue
            result = _run_case(root, cid, sol, tmp / f"work-{cid}", tmp / f"{cid}.json")
            if result is None or "_error" in result:
                unsolved.append(cid)
                rows.append({"case_id": cid, "track": case.get("track"), "status": "RUN_ERROR", "error": (result or {}).get("_error")})
                continue
            hard = result.get("hard_gates", {})
            solved = bool(hard) and all(hard.values())
            row = {
                "case_id": cid,
                "track": case.get("track"),
                "status": "OK" if solved else "UNSOLVED",
                "hard_gates": hard,
                "failing_gates": sorted(k for k, v in hard.items() if not v),
            }
            if not solved:
                unsolved.append(cid)
            if args.gating:
                gate = _gating_check(root, case, tmp)
                if gate is not None:
                    row["gating"] = gate
                    if not gate["gates"]:
                        vacuous.append(cid)
            rows.append(row)

    report = {
        "total": len(cases),
        "certified": sum(1 for r in rows if r["status"] == "OK"),
        "missing_solution": missing,
        "unsolved": unsolved,
        "vacuous_verifiers": vacuous,
        "cases": rows,
    }
    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"oracle_solve: {report['certified']}/{report['total']} certified", file=sys.stderr)
    if missing and not args.allow_missing:
        print(f"  MISSING solutions: {len(missing)} (e.g. {missing[:5]})", file=sys.stderr)
    if unsolved:
        print(f"  UNSOLVED: {unsolved[:10]}", file=sys.stderr)
    if vacuous:
        print(f"  VACUOUS verifiers (do not gate on broken state): {vacuous[:10]}", file=sys.stderr)

    fail = bool(unsolved) or (bool(missing) and not args.allow_missing)
    if not fail:
        print("oracle_solve: ok", file=sys.stderr)
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
