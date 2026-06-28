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
import copy
import json
import os
import pathlib
import re
import shutil
import signal
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
    """Return up to `cap` (description, artifact_text) mutants, sampled EVENLY
    across all mutable sites (not just the first `cap`) so a small cap still
    covers late-file logic."""
    # 1) collect all candidate sites (cheap — no artifact rendering yet)
    sites = []  # (fi, li, name, start, end, repl, line)
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
                if line[: m.start()] + repl + line[m.end():] == line:
                    continue
                sites.append((fi, li, name, m.start(), m.end(), repl, line))
    # 2) even stride down to the cap
    if cap and len(sites) > cap:
        step = len(sites) / cap
        sites = [sites[int(i * step)] for i in range(cap)]
    # 3) render only the chosen mutants
    mutants = []
    for fi, li, name, start, end, repl, line in sites:
        new_files = [(p, list(ls)) for p, ls in files]
        new_files[fi][1][li] = line[:start] + repl + line[end:]
        desc = f"{files[fi][0]}:{li + 1} {name} [{line.strip()[:60]}]"
        mutants.append((desc, render_artifact(new_files)))
    return mutants


def _json_sites(obj: object, path: tuple = ()) -> list[tuple[tuple, str, object]]:
    """Enumerate structural mutation sites over a parsed JSON value.

    Operator mutation (``gen_mutants``) finds nothing in pure-config solutions
    (JSON/YAML have no relational/arithmetic operators), so those cases would
    report 0 mutants and prove nothing about their structural verifiers. These
    sites give config solutions real potency coverage: drop a list element
    (e.g. a pipeline stage or a gate), drop a dict key, rename an identifier
    string (e.g. a gate name), or flip a boolean — each should be caught by a
    verifier that actually reads the config."""
    sites: list[tuple[tuple, str, object]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            sites.append((path, "drop_key", k))
            sites.extend(_json_sites(v, path + (k,)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            sites.append((path, "drop_index", i))
            sites.extend(_json_sites(v, path + (i,)))
    elif isinstance(obj, bool):  # before str/int; bool is an int subclass
        sites.append((path, "flip_bool", obj))
    elif isinstance(obj, str):
        sites.append((path, "rename", obj))
    return sites


def _apply_json_site(obj: object, path: tuple, kind: str, detail: object) -> object:
    """Return a deep copy of `obj` with one structural mutation applied."""
    obj = copy.deepcopy(obj)
    if kind == "drop_key":  # path → the containing dict
        container = obj
        for step in path:
            container = container[step]
        del container[detail]
    elif kind == "drop_index":  # path → the containing list
        container = obj
        for step in path:
            container = container[step]
        container.pop(detail)
    else:  # rename / flip_bool: path → the leaf itself
        parent = obj
        for step in path[:-1]:
            parent = parent[step]
        last = path[-1]
        parent[last] = (detail + "_MUT") if kind == "rename" else (not detail)
    return obj


def gen_config_mutants(files: list[tuple[str, list[str]]], cap: int) -> list[tuple[str, str]]:
    """Structural mutants for JSON config solutions, sampled evenly to `cap`.

    Used only when operator mutation yields nothing (pure-config cases), so it
    is purely additive and never changes a code track's mutant set."""
    sites = []  # (fi, path, kind, detail)
    parsed: dict[int, object] = {}
    for fi, (path, lines) in enumerate(files):
        if _is_test_file(path) or not path.endswith(".json"):
            continue
        try:
            obj = json.loads("\n".join(lines))
        except json.JSONDecodeError:
            continue
        parsed[fi] = obj
        for site in _json_sites(obj):
            sites.append((fi, *site))
    if cap and len(sites) > cap:
        step = len(sites) / cap
        sites = [sites[int(i * step)] for i in range(cap)]
    mutants = []
    for fi, jpath, kind, detail in sites:
        mutated = _apply_json_site(parsed[fi], jpath, kind, detail)
        new_files = [(p, list(ls)) for p, ls in files]
        new_files[fi] = (files[fi][0], json.dumps(mutated, indent=2).splitlines())
        loc = "/".join(str(s) for s in jpath) or "."
        desc = f"{files[fi][0]}:{loc} {kind} [{detail}]"
        mutants.append((desc, render_artifact(new_files)))
    return mutants


def run_mutant(root: pathlib.Path, case_id: str, artifact_text: str, work: pathlib.Path, timeout: int = 25) -> dict:
    """Run one mutant through run_case. The work dir is ALWAYS removed before
    returning (immediate cleanup) so temp never accumulates across the sweep —
    this is what prevents RAM/tmpfs from filling up and freezing the box."""
    work.mkdir(parents=True, exist_ok=True)
    try:
        art = work / "mutant.txt"
        art.write_text(artifact_text, encoding="utf-8")
        out = work / "result.json"
        proc = subprocess.Popen(
            [
                sys.executable, str(root / "runners" / "run_case.py"), case_id,
                "--model", "mutant", "--artifact-file", str(art),
                "--bench-root", str(root), "--work-root", str(work / "ws"), "--out", str(out),
            ],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True,
        )
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            # a mutation that hangs is a behaviour change -> killed. Kill the whole
            # process group so cargo/go/flutter grandchildren don't linger.
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
            proc.wait()
            return {"survived": False, "killer": "timeout"}
        if not out.exists():
            return {"survived": False, "killer": "run_error"}
        hard = json.loads(out.read_text(encoding="utf-8")).get("hard_gates", {})
        if hard and all(hard.values()):
            return {"survived": True, "killer": None}
        return {"survived": False, "killer": "compile" if hard.get("compiles") is False else "test"}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bench_root", nargs="?", default=".")
    parser.add_argument("--track")
    parser.add_argument("--case")
    parser.add_argument("--max-mutants", type=int, default=8)
    parser.add_argument("--timeout", type=int, default=25, help="per-mutant timeout (s); longer for compiled tracks")
    parser.add_argument("--out", default="reports/mutation_test.json")
    args = parser.parse_args()

    root = bench_root(args.bench_root)
    cases = load_cases(root)
    if args.track:
        cases = [c for c in cases if c.get("track") == args.track]
    if args.case:
        cases = [c for c in cases if c.get("id") == args.case]
    solutions = root / "solutions"
    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    survivors = []
    total_mut = total_killed = 0
    done_ids = set()
    # resume a partial/killed run: reload already-scored cases and skip them
    if out_path.exists():
        try:
            prev = json.loads(out_path.read_text(encoding="utf-8"))
            rows = prev.get("per_case", [])
            survivors = prev.get("survivors", [])
            total_mut = int(prev.get("total_mutants", 0) or 0)
            total_killed = int(prev.get("total_killed", 0) or 0)
            done_ids = {r["case_id"] for r in rows}
        except (json.JSONDecodeError, OSError, KeyError):
            pass

    def write_report(complete: bool) -> None:
        out_path.write_text(json.dumps({
            "complete": complete,
            "cases": len(rows),
            "total_mutants": total_mut,
            "total_killed": total_killed,
            "overall_mutation_score": round(total_killed / total_mut, 3) if total_mut else None,
            "survivor_count": len(survivors),
            "survivors": survivors,
            "per_case": rows,
        }, indent=2), encoding="utf-8")

    mut_idx = 0
    with tempfile.TemporaryDirectory(prefix="mut-") as temp:
        tmp = pathlib.Path(temp)
        total = len(cases)
        for ci, case in enumerate(cases, 1):
            cid = case["id"]
            if cid in done_ids:
                continue
            sol = solutions / f"{cid}.txt"
            if not sol.exists():
                continue
            files = parse_artifact(sol.read_text(encoding="utf-8"))
            mutants = gen_mutants(files, args.max_mutants)
            if not mutants:
                # pure-config solution (no code operators) → structural mutation
                mutants = gen_config_mutants(files, args.max_mutants)
            killed = comp = 0
            case_survivors = []
            for desc, text in mutants:
                mut_idx += 1
                res = run_mutant(root, cid, text, tmp / f"m{mut_idx}", timeout=args.timeout)
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
            write_report(complete=False)  # persist after EVERY case → kill-safe
            print(f"[{ci}/{total}] {cid} mutants={len(mutants)} score={score} survivors={len(case_survivors)}", file=sys.stderr, flush=True)

    write_report(complete=True)
    print(f"mutation_test: {len(rows)} cases, {total_mut} mutants, "
          f"score {round(total_killed / total_mut, 3) if total_mut else None}, {len(survivors)} survivors", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
