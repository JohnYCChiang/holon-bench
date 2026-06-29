#!/usr/bin/env python3
"""Stratified calibration sample — pick a small, difficulty-balanced case set.

A full multi-model sweep over all 488 cases is GPU-bound and multi-day. For
difficulty calibration we only need broad, balanced coverage: this picks up to
``--per-track`` cases from EVERY track, spread evenly across the declared
difficulty buckets so each band is represented in each track.

The pick is fully deterministic (fixed difficulty order, case ids sorted within
each bucket, round-robin across buckets) so re-running yields the same set and a
sweep can resume against a stable list. Output feeds ``run_track.py --case-ids``.

Usage: python3 runners/calibration_sample.py . [--per-track 10] [--out reports/calibration_sample.json]
"""
from __future__ import annotations

import argparse
import collections
import json

from common import bench_root, load_cases

# Canonical bucket order; round-robin visits them in turn so harder (fewer) bands
# still get represented before the cap fills with easy/medium cases.
DIFFICULTY_ORDER = ["easy", "medium", "hard", "expert"]


def sample_track(cases: list[dict], per_track: int) -> list[str]:
    """Deterministically pick <= per_track case ids, balanced across difficulty."""
    buckets: dict[str, list[str]] = collections.defaultdict(list)
    for case in cases:
        buckets[case.get("difficulty") or "unknown"].append(case["id"])
    # stable order: known difficulties first (canonical order), then any extras
    order = [d for d in DIFFICULTY_ORDER if d in buckets]
    order += sorted(d for d in buckets if d not in DIFFICULTY_ORDER)
    for d in order:
        buckets[d].sort()
    cursors = {d: 0 for d in order}
    picked: list[str] = []
    progressed = True
    while len(picked) < per_track and progressed:
        progressed = False
        for d in order:
            if len(picked) >= per_track:
                break
            if cursors[d] < len(buckets[d]):
                picked.append(buckets[d][cursors[d]])
                cursors[d] += 1
                progressed = True
    return picked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bench_root", nargs="?", default=".")
    parser.add_argument("--per-track", type=int, default=10)
    parser.add_argument("--out", default="reports/calibration_sample.json")
    args = parser.parse_args()

    root = bench_root(args.bench_root)
    cases = load_cases(root)
    by_track: dict[str, list[dict]] = collections.defaultdict(list)
    for case in cases:
        by_track[case["track"]].append(case)

    sample: dict[str, list[str]] = {}
    for track in sorted(by_track):
        sample[track] = sample_track(by_track[track], args.per_track)

    total = sum(len(ids) for ids in sample.values())
    report = {
        "per_track_cap": args.per_track,
        "tracks": len(sample),
        "total_cases": total,
        "sample": sample,
    }
    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"calibration_sample: {total} cases across {len(sample)} tracks "
          f"(cap {args.per_track}/track) -> {args.out}")
    for track in sorted(sample):
        print(f"  {track}: {len(sample[track])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
