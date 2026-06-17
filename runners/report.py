#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import json
import pathlib

from common import bench_root, load_yaml, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("scores", nargs="+")
    parser.add_argument("--bench-root", default=".")
    args = parser.parse_args()

    root = bench_root(args.bench_root)
    benchmark = load_yaml(root / "manifest/benchmark.yaml")
    minimum_cases = benchmark.get("reporting", {}).get("minimum_cases_for_routing", 5)
    minimum_pass_rate = benchmark.get("reporting", {}).get("minimum_hard_pass_rate_for_routing", 0.6)
    scores = select_final_scores(
        [json.loads(pathlib.Path(path).read_text(encoding="utf-8")) for path in args.scores]
    )
    by_model: dict[str, list[dict]] = collections.defaultdict(list)
    by_model_track: dict[str, dict[str, list[dict]]] = collections.defaultdict(
        lambda: collections.defaultdict(list)
    )
    failures: collections.Counter[str] = collections.Counter()
    for score in scores:
        protocol = score.get("protocol", "patch")
        driver = score.get("driver", "direct")
        label = f"{score['model']} [{protocol}]" if driver == "direct" else f"{score['model']} [{protocol}/{driver}]"
        by_model[label].append(score)
        by_model_track[label][score["track"]].append(score)
        failures.update(score.get("failure_tags", []))

    machine = {}
    per_track = {}
    lines = ["# Holon Benchmark Model Matrix", ""]
    for model, model_scores in sorted(by_model.items()):
        hard_pass_rate = sum(1 for item in model_scores if item["hard_pass"]) / len(model_scores)
        first_pass_rate = sum(1 for item in model_scores if item.get("first_pass")) / len(model_scores)
        final_pass_rate = sum(1 for item in model_scores if item.get("final_pass", item["hard_pass"])) / len(model_scores)
        repair_candidates = [item for item in model_scores if not item.get("first_pass")]
        repaired_count = sum(1 for item in repair_candidates if item.get("repaired_pass"))
        repair_conversion_rate = repaired_count / len(repair_candidates) if repair_candidates else 0.0
        repaired_scores = [item for item in model_scores if item.get("repaired_pass")]
        first_failure_count = len(repair_candidates)
        final_failure_count = sum(
            1 for item in model_scores if not item.get("final_pass", item["hard_pass"])
        )
        total_repair_attempts = sum(int(item.get("repair_attempts_used", 0) or 0) for item in model_scores)
        repair_tax_rate = total_repair_attempts / len(model_scores)
        hidden_case_count = sum(1 for item in model_scores if item.get("has_hidden_verifier"))
        mutation_case_count = sum(1 for item in model_scores if item.get("has_mutation_verifier"))
        governance_levels = collections.Counter(
            item.get("governance_level") or "unknown" for item in model_scores
        )
        generation_paths = collections.Counter(
            item.get("generation_path") or "unknown" for item in model_scores
        )
        fallback_count = sum(1 for item in model_scores if item.get("fallback_used"))
        hidden_failure_count = sum(
            1 for item in model_scores if item.get("has_hidden_verifier") and not item.get("hidden_pass", True)
        )
        mutation_failure_count = sum(
            1 for item in model_scores if item.get("has_mutation_verifier") and not item.get("mutation_pass", True)
        )
        avg_repair_attempts = (
            sum(item.get("repair_attempts_used", 0) for item in repaired_scores) / len(repaired_scores)
            if repaired_scores
            else 0.0
        )
        max_repair_exhausted = sum(1 for item in model_scores if item.get("max_repair_exhausted"))
        soft_avg = sum(item["soft_score"] for item in model_scores) / len(model_scores)
        model_failures: collections.Counter[str] = collections.Counter()
        first_failures: collections.Counter[str] = collections.Counter()
        final_failures: collections.Counter[str] = collections.Counter()
        for item in model_scores:
            model_failures.update(item.get("failure_tags", []))
            first_failures.update(item.get("first_failure_tags", []))
            final_failures.update(item.get("final_failure_tags", item.get("failure_tags", [])))
        tao_truth_chains = collect_tao_truth_chains(model_scores)
        machine[model] = {
            "hard_pass_rate": round(hard_pass_rate, 4),
            "first_pass_rate": round(first_pass_rate, 4),
            "final_pass_rate": round(final_pass_rate, 4),
            "repair_conversion_rate": round(repair_conversion_rate, 4),
            "first_failure_count": first_failure_count,
            "final_failure_count": final_failure_count,
            "repaired_case_count": repaired_count,
            "total_repair_attempts": total_repair_attempts,
            "repair_tax_rate": round(repair_tax_rate, 4),
            "hidden_case_count": hidden_case_count,
            "mutation_case_count": mutation_case_count,
            "governance_levels": dict(governance_levels),
            "generation_paths": dict(generation_paths),
            "fallback_count": fallback_count,
            "hidden_failure_count": hidden_failure_count,
            "mutation_failure_count": mutation_failure_count,
            "avg_repair_attempts_to_pass": round(avg_repair_attempts, 2),
            "max_repair_exhausted_count": max_repair_exhausted,
            "soft_score_avg": round(soft_avg, 2),
            "case_count": len(model_scores),
            "failure_distribution": dict(model_failures),
            "first_failure_distribution": dict(first_failures),
            "final_failure_distribution": dict(final_failures),
            "tao_truth_chains": tao_truth_chains,
        }
        risk_summary = summarize_risks(
            model_scores=model_scores,
            track_scores=by_model_track[model],
            final_failures=final_failures,
            repair_conversion_rate=repair_conversion_rate,
            avg_repair_attempts=avg_repair_attempts,
            max_repair_exhausted=max_repair_exhausted,
            hidden_case_count=hidden_case_count,
            mutation_case_count=mutation_case_count,
        )
        machine[model]["risk_summary"] = risk_summary
        lines.append(f"## {model}")
        lines.append("")
        lines.append(f"- Hard pass rate: {hard_pass_rate:.2%}")
        lines.append(f"- First-pass rate: {first_pass_rate:.2%}")
        lines.append(f"- Final-pass rate: {final_pass_rate:.2%}")
        lines.append(f"- Repair conversion rate: {repair_conversion_rate:.2%}")
        lines.append(f"- Repaired cases: {repaired_count}/{first_failure_count}")
        lines.append(f"- Total repair attempts: {total_repair_attempts}")
        lines.append(f"- Repair tax: {repair_tax_rate:.2f} attempts/case")
        lines.append(f"- Protected/hidden verifier coverage: {hidden_case_count}/{len(model_scores)}")
        lines.append(f"- Mutation verifier coverage: {mutation_case_count}/{len(model_scores)}")
        lines.append(f"- Governance levels: {format_failures(governance_levels)}")
        lines.append(f"- Generation paths: {format_failures(generation_paths)}")
        lines.append(f"- Fallback used: {fallback_count}/{len(model_scores)}")
        lines.append(f"- Hidden/mutation failures: {hidden_failure_count}/{mutation_failure_count}")
        lines.append(f"- Avg repair attempts to pass: {avg_repair_attempts:.2f}")
        lines.append(f"- Max repair exhausted: {max_repair_exhausted}")
        lines.append(f"- Soft score avg: {soft_avg:.2f}")
        lines.append(f"- First failures: {format_failures(first_failures)}")
        lines.append(f"- Final failures: {format_failures(final_failures)}")
        lines.append("")
        append_risk_lines(lines, risk_summary)
        per_track[model] = {}
        for track, track_scores in sorted(by_model_track[model].items()):
            track_pass = sum(1 for item in track_scores if item["hard_pass"]) / len(track_scores)
            track_first_pass = sum(1 for item in track_scores if item.get("first_pass")) / len(track_scores)
            track_final_pass = sum(
                1 for item in track_scores if item.get("final_pass", item["hard_pass"])
            ) / len(track_scores)
            track_repair_candidates = [item for item in track_scores if not item.get("first_pass")]
            track_repaired_count = sum(1 for item in track_repair_candidates if item.get("repaired_pass"))
            track_total_repair_attempts = sum(
                int(item.get("repair_attempts_used", 0) or 0) for item in track_scores
            )
            track_repair_tax = track_total_repair_attempts / len(track_scores)
            track_hidden_case_count = sum(1 for item in track_scores if item.get("has_hidden_verifier"))
            track_mutation_case_count = sum(1 for item in track_scores if item.get("has_mutation_verifier"))
            track_governance_levels = collections.Counter(
                item.get("governance_level") or "unknown" for item in track_scores
            )
            track_generation_paths = collections.Counter(
                item.get("generation_path") or "unknown" for item in track_scores
            )
            track_fallback_count = sum(1 for item in track_scores if item.get("fallback_used"))
            track_hidden_failure_count = sum(
                1 for item in track_scores if item.get("has_hidden_verifier") and not item.get("hidden_pass", True)
            )
            track_mutation_failure_count = sum(
                1 for item in track_scores if item.get("has_mutation_verifier") and not item.get("mutation_pass", True)
            )
            track_repair_conversion = (
                track_repaired_count / len(track_repair_candidates)
                if track_repair_candidates
                else 0.0
            )
            track_final_failures = sum(
                1 for item in track_scores if not item.get("final_pass", item["hard_pass"])
            )
            track_soft = sum(item["soft_score"] for item in track_scores) / len(track_scores)
            track_tao_truth_chains = collect_tao_truth_chains(track_scores)
            per_track[model][track] = {
                "hard_pass_rate": round(track_pass, 4),
                "first_pass_rate": round(track_first_pass, 4),
                "final_pass_rate": round(track_final_pass, 4),
                "repair_conversion_rate": round(track_repair_conversion, 4),
                "first_failure_count": len(track_repair_candidates),
                "final_failure_count": track_final_failures,
                "repaired_case_count": track_repaired_count,
                "total_repair_attempts": track_total_repair_attempts,
                "repair_tax_rate": round(track_repair_tax, 4),
                "hidden_case_count": track_hidden_case_count,
                "mutation_case_count": track_mutation_case_count,
                "governance_levels": dict(track_governance_levels),
                "generation_paths": dict(track_generation_paths),
                "fallback_count": track_fallback_count,
                "hidden_failure_count": track_hidden_failure_count,
                "mutation_failure_count": track_mutation_failure_count,
                "soft_score_avg": round(track_soft, 2),
                "case_count": len(track_scores),
                "tao_truth_chains": track_tao_truth_chains,
            }
            lines.append(f"### {track}")
            lines.append("")
            lines.append(f"- Hard pass rate: {track_pass:.2%}")
            lines.append(f"- First-pass rate: {track_first_pass:.2%}")
            lines.append(f"- Final-pass rate: {track_final_pass:.2%}")
            lines.append(f"- Repair conversion rate: {track_repair_conversion:.2%}")
            lines.append(f"- Repaired cases: {track_repaired_count}/{len(track_repair_candidates)}")
            lines.append(f"- Repair tax: {track_repair_tax:.2f} attempts/case")
            lines.append(f"- Protected/hidden verifier coverage: {track_hidden_case_count}/{len(track_scores)}")
            lines.append(f"- Mutation verifier coverage: {track_mutation_case_count}/{len(track_scores)}")
            lines.append(f"- Governance levels: {format_failures(track_governance_levels)}")
            lines.append(f"- Generation paths: {format_failures(track_generation_paths)}")
            lines.append(f"- Fallback used: {track_fallback_count}/{len(track_scores)}")
            lines.append(f"- Soft score avg: {track_soft:.2f}")
            lines.append("")

    python_artifact_candidates = track_candidates(
        per_track, "python_tool_engineering", minimum_cases, minimum_pass_rate, protocol="artifact"
    )
    rust_artifact_candidates = track_candidates(
        per_track, "rust_core", minimum_cases, minimum_pass_rate, protocol="artifact"
    )
    rust_porting_artifact_candidates = track_candidates(
        per_track, "rust_porting", minimum_cases, minimum_pass_rate, protocol="artifact"
    )
    patch_candidates = routing_candidates(machine, minimum_cases, minimum_pass_rate, protocol="patch")
    routing = {
        "routing": {
            "python_tool_artifact_worker": best_model(python_artifact_candidates),
            "rust_core_artifact_worker": best_model(rust_artifact_candidates),
            "json_contract_generation": "needs contract-specific benchmark scores",
            "patch_generation": best_model(patch_candidates),
            "semantic_review": "needs reviewer-specific benchmark scores",
            "rust_porting": best_model(rust_porting_artifact_candidates),
            "flutter_review": "needs flutter-specific benchmark scores",
            "scope_guard": "needs scope-guard-specific benchmark scores",
        },
        "failure_distribution": dict(failures),
        "note": "golden/oracle runs validate the benchmark pipeline and are not model routing candidates",
        "minimum_cases_for_routing": minimum_cases,
        "minimum_hard_pass_rate_for_routing": minimum_pass_rate,
    }

    (root / "reports").mkdir(exist_ok=True)
    (root / "reports/model_matrix.md").write_text("\n".join(lines), encoding="utf-8")
    write_json(root / "reports/per_track.json", per_track)
    write_json(root / "reports/routing_recommendation.json", routing)
    return 0


def best_model(machine: dict[str, dict]) -> str | None:
    if not machine:
        return "needs model benchmark run"
    return max(machine.items(), key=lambda item: (item[1]["hard_pass_rate"], item[1]["soft_score_avg"]))[0]


def select_final_scores(scores: list[dict]) -> list[dict]:
    selected: dict[tuple[str, str, str, str], dict] = {}
    for score in scores:
        key = (
            str(score.get("model", "")),
            str(score.get("driver", "direct")),
            str(score.get("protocol", "patch")),
            str(score.get("case_id", "")),
        )
        previous = selected.get(key)
        if previous is None or score_rank(score) > score_rank(previous):
            selected[key] = score
    return list(selected.values())


def collect_tao_truth_chains(scores: list[dict]) -> list[dict]:
    chains = []
    for score in scores:
        chain = score.get("tao_truth_chain")
        if isinstance(chain, dict):
            chains.append(
                {
                    "case_id": score.get("case_id"),
                    "track": score.get("track"),
                    "tao_truth_chain": chain,
                }
            )
    return chains


def score_rank(score: dict) -> tuple[int, int, int]:
    return (
        int(score.get("attempt_count", 1) or 1),
        int(score.get("max_repair_attempts", 0) or 0),
        int(bool(score.get("repair_used", False))),
    )


def routing_candidates(
    machine: dict[str, dict], minimum_cases: int, minimum_pass_rate: float, protocol: str
) -> dict[str, dict]:
    return {
        model: metrics
        for model, metrics in machine.items()
        if is_routing_model(model)
        and model_uses_protocol(model, protocol)
        and metrics["case_count"] >= minimum_cases
        and metrics["hard_pass_rate"] >= minimum_pass_rate
    }


def track_candidates(
    per_track: dict[str, dict[str, dict]],
    track: str,
    minimum_cases: int,
    minimum_pass_rate: float,
    protocol: str,
) -> dict[str, dict]:
    return {
        model: tracks[track]
        for model, tracks in per_track.items()
        if is_routing_model(model)
        and model_uses_protocol(model, protocol)
        and track in tracks
        and tracks[track]["case_count"] >= minimum_cases
        and tracks[track]["hard_pass_rate"] >= minimum_pass_rate
    }


def is_routing_model(label: str) -> bool:
    model_name = label.split(" [", 1)[0].lower()
    return model_name not in {"golden", "oracle", "seed-smoke"}


def model_uses_protocol(label: str, protocol: str) -> bool:
    suffix = label.rsplit("[", 1)[-1].rstrip("]") if "[" in label else ""
    return suffix == protocol or suffix.startswith(f"{protocol}/")


def format_failures(failures: collections.Counter[str]) -> str:
    if not failures:
        return "none"
    return ", ".join(f"{tag}={count}" for tag, count in failures.most_common())


def summarize_risks(
    *,
    model_scores: list[dict],
    track_scores: dict[str, list[dict]],
    final_failures: collections.Counter[str],
    repair_conversion_rate: float,
    avg_repair_attempts: float,
    max_repair_exhausted: int,
    hidden_case_count: int,
    mutation_case_count: int,
) -> dict[str, list[str]]:
    risks = {
        "integration": [],
        "deployment": [],
        "operations": [],
    }
    final_pass_rate = sum(
        1 for item in model_scores if item.get("final_pass", item["hard_pass"])
    ) / len(model_scores)

    if final_failures.get("extra_text", 0):
        risks["integration"].append(
            "artifact output sometimes needs recovery; keep strict contract checks and pollution tags enabled"
        )
    if final_failures.get("semantic_check_failed", 0) or final_failures.get("missing_requirement", 0):
        risks["integration"].append(
            "BDD/unit tests are not enough for semantic guarantees; keep hidden semantic verifiers in final gates"
        )
    if final_failures.get("hidden_verifier_failed", 0) or final_failures.get("mutation_verifier_failed", 0):
        risks["integration"].append(
            "public verifiers can pass while hidden or mutation gates fail; expand hidden coverage before treating 100% public pass as production-ready"
        )
    if hidden_case_count < len(model_scores) or mutation_case_count < len(model_scores):
        risks["integration"].append(
            f"protected/hidden and mutation coverage is partial ({hidden_case_count}/{len(model_scores)} protected/hidden, {mutation_case_count}/{len(model_scores)} mutation)"
        )
    for track, scores in sorted(track_scores.items()):
        pass_rate = sum(1 for item in scores if item.get("final_pass", item["hard_pass"])) / len(scores)
        if pass_rate < 0.85:
            risks["integration"].append(
                f"{track} is below 85% final pass rate; do not route production work there without fallback"
            )

    if max_repair_exhausted:
        risks["deployment"].append(
            f"{max_repair_exhausted} cases exhausted repair budget; enforce bounded loops, timeouts, and stop reasons"
        )
    if final_failures.get("compile_fail", 0) or final_failures.get("test_fail", 0):
        risks["deployment"].append(
            "some failures survive repair at compile/test gates; deployment must run verifiers before accepting patches"
        )
    if final_pass_rate < 0.95:
        risks["deployment"].append(
            "final pass rate is below 95%; use staged rollout or human approval for higher-impact changes"
        )

    if repair_conversion_rate > 0 and avg_repair_attempts > 1.5:
        risks["operations"].append(
            "repair convergence takes multiple attempts; budget token, wall-clock, and retry limits per case"
        )
    if repair_conversion_rate > 0:
        risks["operations"].append(
            "track first-pass and repaired-pass separately; repaired success is useful but has higher operating cost"
        )
    if final_failures.get("timeout", 0) or final_failures.get("resource_leak", 0):
        risks["operations"].append(
            "timeout/resource failures observed; keep process-group cancellation and resource guards active"
        )

    for category, items in risks.items():
        if not items:
            risks[category].append("no material risk flagged by current benchmark signals")
    return risks


def append_risk_lines(lines: list[str], risk_summary: dict[str, list[str]]) -> None:
    lines.append("### Risk Summary")
    lines.append("")
    for category in ("integration", "deployment", "operations"):
        label = category.title()
        lines.append(f"- {label}: {risk_summary[category][0]}")
        for item in risk_summary[category][1:]:
            lines.append(f"- {label}: {item}")
    lines.append("")


if __name__ == "__main__":
    raise SystemExit(main())
