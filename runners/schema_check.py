#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from common import bench_root, load_cases, load_yaml


REQUIRED_CASE_FIELDS = {
    "id",
    "track",
    "language",
    "difficulty",
    "task_type",
    "fixture",
    "user_request",
    "constraints",
    "allowed_paths",
    "forbidden_paths",
    "verifier",
    "scoring",
    "failure_tags",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bench_root", nargs="?", default=".")
    args = parser.parse_args()

    root = bench_root(args.bench_root)
    benchmark = load_yaml(root / "manifest/benchmark.yaml")
    tracks = load_yaml(root / "manifest/tracks.yaml")["tracks"]
    scoring = load_yaml(root / "manifest/scoring.yaml")
    taxonomy = load_yaml(root / "manifest/failure_taxonomy.yaml")["failure_types"]
    known_failures = {tag for tags in taxonomy.values() for tag in tags}
    known_roles = set(scoring.get("role_scores", {}))

    errors: list[str] = []
    seen_ids: set[str] = set()
    cases = load_cases(root)
    for track_name, track in tracks.items():
        for role in track.get("role_focus", []):
            if role not in known_roles:
                errors.append(f"tracks.{track_name}: unknown role_focus {role}")

    phase_1_track_target = sum(int(track.get("phase_1_cases", 0) or 0) for track in tracks.values())
    if int(benchmark["case_count_target"].get("phase_1", 0) or 0) != phase_1_track_target:
        errors.append(
            "phase_1 case_count_target expected "
            f"{phase_1_track_target} from tracks.yaml, found {benchmark['case_count_target'].get('phase_1')}"
        )

    for case in cases:
        missing = REQUIRED_CASE_FIELDS - set(case)
        if missing:
            errors.append(f"{case.get('id', '<unknown>')}: missing fields {sorted(missing)}")
        if case.get("id") in seen_ids:
            errors.append(f"{case['id']}: duplicate case id")
        seen_ids.add(case.get("id", ""))
        if case.get("track") not in tracks:
            errors.append(f"{case.get('id')}: unknown track {case.get('track')}")
        verifier = case.get("verifier", {})
        if not verifier.get("commands"):
            errors.append(f"{case.get('id')}: verifier.commands must not be empty")
        scoring = case.get("scoring", {})
        if not scoring.get("hard_gates"):
            errors.append(f"{case.get('id')}: scoring.hard_gates must not be empty")
        unknown_tags = [tag for tag in case.get("failure_tags", []) if tag not in known_failures]
        if unknown_tags:
            errors.append(f"{case.get('id')}: unknown failure tags {unknown_tags}")

    phase = str(benchmark.get("phase", "phase_1_mini_core"))
    if phase.startswith("phase_2"):
        target_key = "phase_2"
    elif phase.startswith("phase_3"):
        target_key = "phase_3"
    elif phase.startswith("phase_4"):
        target_key = "phase_4"
    else:
        target_key = "phase_1"
    expected = benchmark["case_count_target"][target_key]
    if len(cases) != expected:
        errors.append(f"{target_key} case count expected {expected}, found {len(cases)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"schema_check: ok ({len(cases)} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
