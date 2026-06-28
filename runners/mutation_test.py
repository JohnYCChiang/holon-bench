#!/usr/bin/env python3
"""Mutation potency testing — prove the verifiers actually catch bugs.

The golden-solve oracle proves each case is *solvable*. This proves the
verifiers are *potent*: it takes a case's certified reference solution
(``solutions/<id>.txt``), injects small semantic mutations one at a time, and
re-runs the full verifier suite (visible + hidden + mutation) on each mutant.

  - A mutant that makes a verifier FAIL is "killed" (good — the suite catches
    that class of bug).
  - A mutant that still PASSES every hard gate "survives" — the verifiers did
    not notice the behavioural change, i.e. a GAP worth hardening.

Mutants that fail to compile are killed trivially (reported separately). The
interesting signal is survivors that compiled and still passed.

This is heavy (one run_case per mutant). Use ``--track``/``--case`` and
``--max-mutants`` to bound it; run off the critical path.

Usage: python3 runners/mutation_test.py . [--track T | --case ID] [--max-mutants N]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import tempfile

from common import bench_root, load_cases

# (name, regex, replacement). Applied only to code (non-comment) lines.
OPERATORS = [
    ("eq->ne", re.compile(r"(?<![<>=!])==(?!=)"), "!="),
    ("ne->eq", re.compile(r"!="), "=="),
    ("le->lt", re.compile(r"<="), "<"),
    ("ge->gt", re.compile(r">="), ">"),
    ("lt->le", re.compile(r"(?<![<>=!])<(?![=<])"), "<="),
    ("gt->ge", re.compile(r"(?<![<>=!])>(?![=>])"), ">="),
    ("and->or", re.compile(r"\band\b"), "or"),
    ("or->and", re.compile(r"\bor\b"), "and"),
    ("&&->||", re.compile(r"&&"), "||"),
    ("||->&&", re.compile(r"\|\|"), "&&"),
    ("add->sub", re.compile(r"(?<![+\-0-9])\+(?![+=])"), "-"),
    ("sub->add", re.compile(r"(?<![+\-0-9])-(?![-=>0-9])"), "+"),
    ("true->false", re.compile(r"\bTrue\b"), "False"),
    ("false->true", re.compile(r"\bFalse\b"), "True"),
    ("min->max", re.compile(r"\.min\("), ".max("),
    ("max->min", re.compile(r"\.max\("), ".min("),
]

COMMENT_PREFIXES = ("#", "//", "///", "*", "/*")


def _is_code_line(line: str) -> bool:
    s = line.strip()
    return bool(s) and not s.startswith(COMMENT_PREFIXES)


def _is_test_file(path: str) -> bool:
    base = path.rsplit("/", 1)[-1]
    return path.startswith("tests/") or "/tests/" in path or base.startswith("test_") or "_test." in base


def _inside_string(line: str, pos: int) -> bool:
    """Rough: a match at pos is inside a quoted string if an odd number of
    unescaped quotes precede it."""
    prefix = line[:pos]
    return (prefix.count('"') - prefix.count('\\"')) % 2 == 1 or (prefix.count("'") - prefix.count("\\'")) % 2 == 1


def parse_artifact(text: str) -> list[tuple[str, list[str]]]:
    """Return [(path, [lines]), ...] from a --- FILE: --- artifact."""
    parts = re.split(r"--- FILE: (.*?) ---\n", text)
    files = []
    for path, body in zip(parts[1::2], parts[2::2]):
        files.append((path.strip(), body.splitlines()))
    return files


def render_artifact(files: list[tuple[str, list[str]]]) -> str:
    out = []
    for path, lines in files:
        out.append(f"--- FILE: {path} ---")
        out.extend(lines)
    return "\n".join(out) + "\n"


def gen_mutants(files: list[tuple[str, list[str]]], cap: int) -> list[tuple[str, str]]:
    """Yield (description, artifact_text) — each with exactly one token mutated."""
    mutants = []
    for fi, (path, lines) in enumerate(files):
        if _is_test_file(path):
            continue  # mutate the source logic, not an authored test
        in_doc = False
        for li, line in enumerate(lines):
            triple = line.count('"""') + line.count("'''")
            if in_doc:
                if triple % 2 == 1:
                    in_doc = False
                continue
            if triple % 2 == 1:
                in_doc = True
                continue
            if not _is_code_line(line):
                continue
            for name, pattern, repl in OPERATORS:
                m = pattern.search(line)
                if not m or _inside_string(line, m.start()):
                    continue
                mutated_line = line[: m.start()] + repl + line[m.end():]
                if mutated_line == line:
                    continue
                new_files = [(p, list(ls)) for p, ls in files]
                new_files[fi][1][li] = mutated_line
                desc = f"{path}:{li + 1} {name} [{line.strip()[:60]}]"
                mutants.append((desc, render_artifact(new_files)))
                if len(mutants) >= cap:
                    return mutants
    return mutants


def run_mutant(root: pathlib.Path, case_id: str, artifact_text: str, work: pathlib.Path) -> dict:
    work.mkdir(parents=True, exist_ok=True)
    art = work / "mutant.txt"
    art.write_text(artifact_text, encoding="utf-8")
    out = work / "result.json"
    subprocess.run(
        [
            sys.executable, str(root / "runners" / "run_case.py"), case_id,
            "--model", "mutant", "--artifact-file", str(art),
            "--bench-root", str(root), "--work-root", str(work / "ws"), "--out", str(out),
        ],
        capture_output=True, text=True,
    )
    if not out.exists():
        return {"survived": False, "killer": "run_error"}
    hard = json.loads(out.read_text(encoding="utf-8")).get("hard_gates", {})
    if hard and all(hard.values()):
        return {"survived": True, "killer": None}
    killer = "compile" if hard.get("compiles") is False else "test"
    return {"survived": False, "killer": killer}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bench_root", nargs="?", default=".")
    parser.add_argument("--track")
    parser.add_argument("--case")
    parser.add_argument("--max-mutants", type=int, default=8)
    parser.add_argument("--out", default="reports/mutation_test.json")
    args = parser.parse_args()

    root = bench_root(args.bench_root)
    cases = load_cases(root)
    if args.track:
        cases = [c for c in cases if c.get("track") == args.track]
    if args.case:
        cases = [c for c in cases if c.get("id") == args.case]
    solutions = root / "solutions"

    rows = []
    survivors = []
    total_mut = total_killed = 0
    mut_idx = 0
    with tempfile.TemporaryDirectory(prefix="mut-") as temp:
        tmp = pathlib.Path(temp)
        for case in cases:
            cid = case["id"]
            sol = solutions / f"{cid}.txt"
            if not sol.exists():
                continue
            files = parse_artifact(sol.read_text(encoding="utf-8"))
            mutants = gen_mutants(files, args.max_mutants)
            killed = comp = 0
            case_survivors = []
            for desc, text in mutants:
                mut_idx += 1
                res = run_mutant(root, cid, text, tmp / f"m{mut_idx}")
                if res["survived"]:
                    case_survivors.append(desc)
                    survivors.append({"case_id": cid, "mutation": desc})
                else:
                    killed += 1
                    if res["killer"] == "compile":
                        comp += 1
            total_mut += len(mutants)
            total_killed += killed
            score = round(killed / len(mutants), 3) if mutants else None
            rows.append({
                "case_id": cid, "track": case["track"], "mutants": len(mutants),
                "killed": killed, "killed_by_compile": comp, "survived": len(case_survivors),
                "mutation_score": score, "survivors": case_survivors,
            })

    report = {
        "cases": len(rows),
        "total_mutants": total_mut,
        "total_killed": total_killed,
        "overall_mutation_score": round(total_killed / total_mut, 3) if total_mut else None,
        "survivor_count": len(survivors),
        "survivors": survivors,
        "per_case": rows,
    }
    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"mutation_test: {len(rows)} cases, {total_mut} mutants, "
          f"score {report['overall_mutation_score']}, {len(survivors)} survivors", file=sys.stderr)
    for s in survivors[:15]:
        print(f"  SURVIVED {s['case_id']}: {s['mutation']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
