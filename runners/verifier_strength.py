#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import pathlib

from common import bench_root, load_cases, verifier_strength, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bench-root", default=".")
    parser.add_argument("--json-out", default="reports/verifier_strength.json")
    parser.add_argument("--md-out", default="reports/verifier_strength.md")
    args = parser.parse_args()

    root = bench_root(args.bench_root)
    cases = load_cases(root)
    rows = []
    by_track: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    totals: collections.Counter[str] = collections.Counter()
    for case in cases:
        strength = verifier_strength(case)
        row = {
            "id": case["id"],
            "track": case["track"],
            "difficulty": case.get("difficulty"),
            "task_type": case.get("task_type"),
            **strength,
        }
        rows.append(row)
        by_track[case["track"]][strength["tier"]] += 1
        by_track[case["track"]]["total"] += 1
        totals[strength["tier"]] += 1
        totals["total"] += 1

    weak_cases = [
        row
        for row in rows
        if not row["has_hidden_verifier"]
        or not row["has_verifier_commands"]
        or row["tier"] == "basic"
    ]
    no_semantic_gate = [
        row for row in rows if row["has_semantic_checks"] and not row["semantic_gate_declared"]
    ]

    write_json(
        root / args.json_out,
        {
            "summary": {
                "total": totals["total"],
                "strong": totals["strong"],
                "standard": totals["standard"],
                "basic": totals["basic"],
                "weak_case_count": len(weak_cases),
                "semantic_checks_without_gate": len(no_semantic_gate),
            },
            "by_track": {track: dict(counter) for track, counter in sorted(by_track.items())},
            "cases": rows,
            "weak_cases": weak_cases,
            "semantic_checks_without_gate": no_semantic_gate,
        },
    )
    (root / args.md_out).write_text(render_markdown(rows, by_track, totals), encoding="utf-8")
    print(root / args.md_out)
    print(root / args.json_out)
    return 0


def render_markdown(
    rows: list[dict], by_track: dict[str, collections.Counter[str]], totals: collections.Counter[str]
) -> str:
    lines = [
        "# Holon-Bench Verifier Strength",
        "",
        "## Summary",
        "",
        f"- Total cases: {totals['total']}",
        f"- Strong: {totals['strong']}",
        f"- Standard: {totals['standard']}",
        f"- Basic: {totals['basic']}",
        "",
        "Strength scoring: verifier command + protected verifier assets + hidden/protected tests + semantic checks + declared scope/safety/semantic gates.",
        "",
        "## By Track",
        "",
        "| Track | Total | Strong | Standard | Basic |",
        "|---|---:|---:|---:|---:|",
    ]
    for track, counter in sorted(by_track.items()):
        lines.append(
            f"| {track} | {counter['total']} | {counter['strong']} | {counter['standard']} | {counter['basic']} |"
        )

    lines += [
        "",
        "## Case Matrix",
        "",
        "| Case | Track | Tier | Score | Hidden | Semantic | Scope | Safety | Commands |",
        "|---|---|---:|---:|---|---|---|---|---:|",
    ]
    for row in rows:
        lines.append(
            "| {id} | {track} | {tier} | {score} | {hidden} | {semantic} | {scope} | {safety} | {commands} |".format(
                id=row["id"],
                track=row["track"],
                tier=row["tier"],
                score=row["score"],
                hidden=hidden_label(row),
                semantic=", ".join(row["semantic_checks"]) if row["semantic_checks"] else "-",
                scope=yes(row["scope_gate_declared"]),
                safety=yes(row["safety_gate_declared"]),
                commands=(
                    row["verifier_command_count"]
                    + row.get("hidden_command_count", 0)
                    + row.get("mutation_command_count", 0)
                ),
            )
        )
    return "\n".join(lines) + "\n"


def yes(value: bool) -> str:
    return "yes" if value else "no"


def hidden_label(row: dict) -> str:
    labels = []
    if row["has_hidden_verifier"]:
        labels.append("hidden")
    if row.get("has_mutation_verifier"):
        labels.append("mutation")
    return "+".join(labels) if labels else "no"


if __name__ == "__main__":
    raise SystemExit(main())
