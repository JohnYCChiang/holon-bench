#!/usr/bin/env python3
"""Difficulty calibration & discriminative-power analysis.

From committed model result/score sets, compute each case's empirical pass rate
across models, cross-check against the golden-solve oracle, and flag:

  - saturated  : every model passes (low discriminative power — case too easy / a
                 candidate to retire or harden), among cases with enough models.
  - unbeaten   : no model passes. The oracle proves the case IS solvable (its
                 reference solution certifies), so an unbeaten case is genuinely
                 hard — unless the oracle also failed it, which would mean BROKEN.
  - difficulty_mismatch : declared difficulty contradicts the empirical pass rate
                 (e.g. an "easy" case no model solves, or an "expert" all solve).

Also reports empirical pass rate per declared difficulty band. Cases without
model runs yet (e.g. the freshly-added ones) are counted as "no_data".

Usage: python3 runners/calibration.py . [score_or_result_json ...]
  (defaults to reports/*_score.json). --oracle reports/oracle_full.json
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import pathlib

from common import bench_root, load_cases

MIN_MODELS = 3  # need at least this many models before judging discriminative power

# declared difficulty -> (min plausible pass rate, max plausible pass rate)
DIFFICULTY_BANDS = {
    "easy": (0.55, 1.01),
    "medium": (0.30, 1.01),
    "hard": (0.05, 0.90),
    "expert": (0.0, 0.70),
}


def load_case_passes(score_paths: list[str]) -> dict[str, dict[str, bool]]:
    """case_id -> {model: solved} where solved = any pass (final or hard) for that model."""
    passes: dict[str, dict[str, bool]] = collections.defaultdict(dict)
    for path in score_paths:
        try:
            data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        cid = data.get("case_id")
        model = data.get("model")
        if not cid or not model or model in {"oracle", "dummy", "seed-smoke", "ci-smoke"}:
            continue
        solved = bool(data.get("final_pass", data.get("hard_pass", False)))
        passes[cid][model] = passes[cid].get(model, False) or solved
    return passes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bench_root", nargs="?", default=".")
    parser.add_argument("scores", nargs="*", help="score/result json (default reports/*_score.json)")
    parser.add_argument("--oracle", default="reports/oracle_full.json")
    parser.add_argument("--min-models", type=int, default=MIN_MODELS)
    parser.add_argument("--out", default="reports/calibration.json")
    args = parser.parse_args()

    root = bench_root(args.bench_root)
    score_paths = args.scores or sorted(glob.glob(str(root / "reports/*_score.json")))
    passes = load_case_passes(score_paths)

    oracle_certified: dict[str, bool] = {}
    oracle_path = root / args.oracle
    if oracle_path.exists():
        oracle = json.loads(oracle_path.read_text(encoding="utf-8"))
        for row in oracle.get("cases", []):
            oracle_certified[row["case_id"]] = row.get("status") == "OK"

    cases = load_cases(root)
    per_difficulty: dict[str, list[float]] = collections.defaultdict(list)
    saturated, unbeaten, broken, mismatched = [], [], [], []
    no_data = 0
    rows = []

    for case in cases:
        cid = case["id"]
        difficulty = case.get("difficulty")
        model_passes = passes.get(cid, {})
        n_models = len(model_passes)
        if n_models == 0:
            no_data += 1
            continue
        n_pass = sum(1 for solved in model_passes.values() if solved)
        rate = round(n_pass / n_models, 4)
        per_difficulty[difficulty].append(rate)
        certified = oracle_certified.get(cid, True)
        row = {"case_id": cid, "track": case["track"], "difficulty": difficulty,
               "models": n_models, "pass_rate": rate, "oracle_certified": certified}
        rows.append(row)

        if n_models >= args.min_models:
            if rate >= 1.0:
                saturated.append(row)
            elif rate <= 0.0:
                (broken if not certified else unbeaten).append(row)
            band = DIFFICULTY_BANDS.get(difficulty)
            if band and not (band[0] <= rate <= band[1]):
                mismatched.append({**row, "expected_band": band})

    difficulty_summary = {
        d: {
            "cases_with_data": len(rates),
            "mean_pass_rate": round(sum(rates) / len(rates), 4) if rates else None,
        }
        for d, rates in sorted(per_difficulty.items())
    }

    report = {
        "models_seen": sorted({m for mp in passes.values() for m in mp}),
        "cases_with_data": len(rows),
        "cases_without_data": no_data,
        "min_models_for_judgement": args.min_models,
        "pass_rate_by_declared_difficulty": difficulty_summary,
        "saturated": saturated,
        "unbeaten_but_solvable": unbeaten,
        "broken_oracle_uncertified": broken,
        "difficulty_mismatch": mismatched,
    }
    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"calibration: {len(rows)} cases with data, {no_data} without "
          f"({len(report['models_seen'])} models)")
    print(f"  pass rate by difficulty: "
          + ", ".join(f"{d}={v['mean_pass_rate']}" for d, v in difficulty_summary.items()))
    print(f"  saturated={len(saturated)} unbeaten={len(unbeaten)} "
          f"broken={len(broken)} difficulty_mismatch={len(mismatched)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
