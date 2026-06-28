#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib

from common import bench_root, load_yaml, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result_json")
    parser.add_argument("--bench-root", default=".")
    parser.add_argument("--out", default="reports/case_score.json")
    args = parser.parse_args()

    root = bench_root(args.bench_root)
    scoring = load_yaml(root / "manifest/scoring.yaml")
    result = json.loads(pathlib.Path(args.result_json).read_text(encoding="utf-8"))
    hard_gates = result["hard_gates"]
    diff = result.get("diff_analysis", {})
    strength = result.get("verifier_strength", {})
    generation = result.get("generation_trace", {}) or {}
    hard_pass = all(hard_gates.values())
    attempt_count = int(result.get("attempt_count", 1) or 1)
    repair_used = bool(result.get("repair_used", False))
    first_pass = bool(result.get("first_pass", hard_pass if not repair_used else False))
    final_pass = bool(result.get("final_pass", hard_pass))
    repair_attempts_used = int(
        result.get("repair_attempts_used", max(0, attempt_count - 1) if repair_used else 0) or 0
    )
    max_repair_attempts = int(result.get("max_repair_attempts", repair_attempts_used) or 0)
    repaired_pass = bool(result.get("repaired_pass", final_pass and not first_pass))
    max_repair_exhausted = (
        (not final_pass) and max_repair_attempts > 0 and repair_attempts_used >= max_repair_attempts
    )

    governance_checks = result.get("governance_checks") or []
    governance_failures = [
        str(check.get("name", f"governance_check_{index}"))
        for index, check in enumerate(governance_checks)
        if isinstance(check, dict) and not check.get("passed", True)
    ]

    weights = scoring["soft_score"]
    soft = 0
    if hard_gates.get("tests_pass"):
        soft += weights["functional_correctness"]
    if hard_gates.get("schema_valid"):
        soft += weights["contract_compliance"]
    if hard_gates.get("scope_pass"):
        soft += weights["scope_disciplined"]
    changed_count = len(result.get("changed_files", []))
    if changed_count <= 3 and hard_gates.get("patch_applies"):
        soft += weights["minimality"]
    if hard_gates.get("compiles"):
        soft += weights["maintainability"]
    if hard_gates.get("tests_pass"):
        soft += weights["test_quality"]
    if not result.get("failure_tags"):
        soft += weights["observability"]

    porting_signal = 0.0
    if result["track"] == "rust_porting":
        porting_signal = (
            score_bool(hard_gates.get("tests_pass")) * 0.5
            + score_bool(hard_gates.get("schema_valid")) * 0.25
            + score_bool(hard_gates.get("scope_pass")) * 0.25
        )

    # game_system / cross_platform are track-specific roles (mirroring porting_signal):
    # they only carry signal on the tracks that exercise them, else 0.0.
    game_signal = 0.0
    if result["track"] in ("go_game_server", "martial_rpg", "rust_bevy"):
        # tick/state correctness (tests) + deterministic state under hidden cases
        # (hidden_pass) + boundary/authority potency (mutation_pass).
        game_signal = (
            score_bool(hard_gates.get("tests_pass")) * 0.4
            + score_bool(hard_gates.get("hidden_pass")) * 0.3
            + score_bool(hard_gates.get("mutation_pass")) * 0.3
        )
    cross_platform_signal = 0.0
    if result["track"] == "flutter_cross_platform":
        # widget/logic tests + platform/async-lifecycle edge cases (hidden) +
        # platform-abstraction discipline (scope).
        cross_platform_signal = (
            score_bool(hard_gates.get("tests_pass")) * 0.4
            + score_bool(hard_gates.get("hidden_pass")) * 0.3
            + score_bool(hard_gates.get("scope_pass")) * 0.3
        )

    role_signals = {
        "contract_worker": score_bool(hard_gates.get("schema_valid")) * 0.5 + score_bool(hard_gates.get("scope_pass")) * 0.5,
        "patch_worker": score_bool(hard_gates.get("patch_applies")) * 0.3 + score_bool(hard_gates.get("tests_pass")) * 0.7,
        # reviewer: scope-violation detection (scope_pass) + semantic-bug detection /
        # behaviour preservation (hidden_pass) + risk identification via regression tests.
        "reviewer": (
            score_bool(hard_gates.get("scope_pass")) * 0.4
            + score_bool(hard_gates.get("hidden_pass")) * 0.4
            + score_bool(diff.get("has_regression_test_signal")) * 0.2
        ),
        # planner: correct decomposition shows as first-pass success (no repair needed) +
        # scope-boundary accuracy + verifier awareness (tests pass).
        "planner": (
            score_bool(first_pass) * 0.4
            + score_bool(hard_gates.get("scope_pass")) * 0.3
            + score_bool(hard_gates.get("tests_pass")) * 0.3
        ),
        "tool_maker": (
            score_bool(hard_gates.get("schema_valid")) * 0.4
            + score_bool(hard_gates.get("tests_pass")) * 0.4
            + score_bool(diff.get("has_regression_test_signal")) * 0.2
        ),
        "porting_worker": porting_signal,
        "game_system_worker": game_signal,
        "cross_platform_app_worker": cross_platform_signal,
    }

    score = {
        "case_id": result["case_id"],
        "track": result["track"],
        "task_type": result["task_type"],
        "model": result["model"],
        "protocol": result["protocol"],
        "driver": result.get("driver", "direct"),
        "generation_path": result.get("generation_path"),
        "governance_level": result.get("governance_level"),
        "governance_mode": result.get("governance_mode"),
        "governance_check_count": len(governance_checks),
        "governance_failure_count": len(governance_failures),
        "governance_failures": governance_failures,
        "fallback_used": result.get("fallback_used"),
        "workflow_attempted": result.get("workflow_attempted"),
        "workflow_type": result.get("workflow_type"),
        "prompt_stack": result.get("prompt_stack"),
        "tao_truth_chain": result.get("tao_truth_chain"),
        "attempt_count": attempt_count,
        "repair_used": repair_used,
        "first_pass": first_pass,
        "final_pass": final_pass,
        "repaired_pass": repaired_pass,
        "repair_attempts_used": repair_attempts_used,
        "max_repair_attempts": max_repair_attempts,
        "max_repair_exhausted": max_repair_exhausted,
        "hard_pass": hard_pass,
        "has_hidden_verifier": bool(strength.get("has_hidden_verifier")),
        "has_mutation_verifier": bool(strength.get("has_mutation_verifier")),
        "hidden_pass": bool(hard_gates.get("hidden_pass", True)),
        "mutation_pass": bool(hard_gates.get("mutation_pass", True)),
        "gates_passed_count": sum(1 for value in hard_gates.values() if value),
        "gates_total": len(hard_gates),
        "completion_tokens": generation.get("completion_tokens"),
        "truncated": bool(generation.get("truncated", False)),
        "soft_score": min(100, soft),
        "regression_test_signal": bool(diff.get("has_regression_test_signal")),
        "added_test_count": int(diff.get("added_test_count", 0) or 0),
        "added_assertion_count": int(diff.get("added_assertion_count", 0) or 0),
        "role_signals": role_signals,
        "failure_tags": result.get("failure_tags", []),
        "first_failure_tags": result.get("first_failure_tags", []),
        "final_failure_tags": result.get("final_failure_tags", result.get("failure_tags", [])),
    }
    out = root / args.out
    write_json(out, score)
    print(out)
    return 0


def score_bool(value: object) -> float:
    return 1.0 if value else 0.0


if __name__ == "__main__":
    raise SystemExit(main())
