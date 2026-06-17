from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import report
import score_case


def write_manifest(root: pathlib.Path) -> None:
    manifest = root / "manifest"
    manifest.mkdir()
    (manifest / "benchmark.yaml").write_text("reporting: {}\n", encoding="utf-8")
    (manifest / "scoring.yaml").write_text(
        """
soft_score:
  functional_correctness: 40
  contract_compliance: 20
  scope_disciplined: 20
  minimality: 5
  maintainability: 5
  test_quality: 5
  observability: 5
""".lstrip(),
        encoding="utf-8",
    )


def minimal_result(**overrides: object) -> dict:
    result = {
        "case_id": "case-1",
        "track": "python_tool_engineering",
        "task_type": "bugfix",
        "model": "m",
        "protocol": "patch",
        "hard_gates": {
            "patch_applies": True,
            "compiles": True,
            "tests_pass": True,
            "schema_valid": True,
            "scope_pass": True,
            "safety_pass": True,
            "semantic_pass": True,
            "hidden_pass": True,
            "mutation_pass": True,
        },
        "diff_analysis": {},
        "verifier_strength": {},
        "changed_files": [],
        "failure_tags": [],
    }
    result.update(overrides)
    return result


def score_result(root: pathlib.Path, result: dict) -> dict:
    result_path = root / "result.json"
    score_path = root / "score.json"
    result_path.write_text(json.dumps(result), encoding="utf-8")
    with mock.patch.object(
        sys,
        "argv",
        ["score_case.py", str(result_path), "--bench-root", str(root), "--out", str(score_path)],
    ):
        assert score_case.main() == 0
    return json.loads(score_path.read_text(encoding="utf-8"))


def base_score(**overrides: object) -> dict:
    score = {
        "case_id": "case-1",
        "track": "python_tool_engineering",
        "task_type": "bugfix",
        "model": "m",
        "protocol": "patch",
        "driver": "holon-cli",
        "hard_pass": True,
        "soft_score": 100,
        "role_signals": {},
        "attempt_count": 1,
        "repair_used": False,
        "first_pass": True,
        "final_pass": True,
        "repaired_pass": False,
        "repair_attempts_used": 0,
        "max_repair_attempts": 0,
        "max_repair_exhausted": False,
        "has_hidden_verifier": True,
        "has_mutation_verifier": False,
        "hidden_pass": True,
        "mutation_pass": True,
        "failure_tags": [],
        "final_failure_tags": [],
        "governance_failure_count": 0,
    }
    score.update(overrides)
    return score


class GovernanceScoreTests(unittest.TestCase):
    def test_score_records_governance_mode_and_failures(self) -> None:
        result = minimal_result(
            governance_mode="governed",
            governance_checks=[
                {"name": "scope_guard", "passed": True},
                {"name": "tao_truth_chain_complete", "passed": False},
            ],
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            write_manifest(root)
            score = score_result(root, result)
        self.assertEqual(score["governance_mode"], "governed")
        self.assertEqual(score["governance_check_count"], 2)
        self.assertEqual(score["governance_failure_count"], 1)
        self.assertEqual(score["governance_failures"], ["tao_truth_chain_complete"])

    def test_score_keeps_legacy_results_without_governance_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            write_manifest(root)
            score = score_result(root, minimal_result())
        self.assertIsNone(score["governance_mode"])
        self.assertEqual(score["governance_check_count"], 0)
        self.assertEqual(score["governance_failure_count"], 0)
        self.assertEqual(score["governance_failures"], [])


class GovernanceComparisonTests(unittest.TestCase):
    def test_matched_comparison_summarizes_behavior_deltas(self) -> None:
        scores = [
            base_score(
                case_id="case-1",
                governance_mode="governed",
                repair_attempts_used=0,
                hidden_pass=True,
                final_failure_tags=[],
                governance_failure_count=0,
            ),
            base_score(
                case_id="case-1",
                governance_mode="ungoverned",
                repair_attempts_used=2,
                hidden_pass=False,
                final_pass=False,
                hard_pass=False,
                final_failure_tags=["over_refactor", "hidden_verifier_failed"],
                governance_failure_count=0,
            ),
        ]
        comparison = report.build_governance_comparison(scores)
        self.assertIsNotNone(comparison)
        self.assertEqual(comparison["matched_case_count"], 1)
        self.assertEqual(comparison["governed"]["scope_drift_rate"], 0.0)
        self.assertEqual(comparison["ungoverned"]["scope_drift_rate"], 1.0)
        self.assertEqual(comparison["ungoverned"]["repair_tax_rate"], 2.0)
        self.assertEqual(comparison["ungoverned"]["hidden_pass_rate"], 0.0)
        deltas = comparison["deltas"]
        self.assertEqual(deltas["scope_drift_rate"], -1.0)
        self.assertEqual(deltas["repair_tax_rate"], -2.0)
        self.assertEqual(deltas["hidden_pass_rate"], 1.0)

    def test_unmatched_modes_still_report_per_group(self) -> None:
        scores = [
            base_score(case_id="case-1", governance_mode="governed"),
            base_score(case_id="case-2", governance_mode="ungoverned"),
        ]
        comparison = report.build_governance_comparison(scores)
        self.assertEqual(comparison["matched_case_count"], 0)
        self.assertNotIn("deltas", comparison)
        self.assertEqual(comparison["governed"]["case_count"], 1)
        self.assertEqual(comparison["ungoverned"]["case_count"], 1)

    def test_legacy_scores_without_governance_mode_produce_no_comparison(self) -> None:
        scores = [base_score(case_id="case-1"), base_score(case_id="case-2")]
        self.assertIsNone(report.build_governance_comparison(scores))

    def test_report_writes_comparison_artifact_and_section(self) -> None:
        scores = [
            base_score(case_id="case-1", driver="holon-cli", governance_mode="governed"),
            base_score(
                case_id="case-1",
                driver="direct",
                governance_mode="ungoverned",
                repair_attempts_used=1,
                final_failure_tags=["over_refactor"],
                governance_failure_count=1,
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            write_manifest(root)
            score_paths = []
            for index, score in enumerate(scores):
                path = root / f"score-{index}.json"
                path.write_text(json.dumps(score), encoding="utf-8")
                score_paths.append(str(path))
            with mock.patch.object(
                sys, "argv", ["report.py", *score_paths, "--bench-root", str(root)]
            ):
                self.assertEqual(report.main(), 0)
            comparison = json.loads(
                (root / "reports" / "governance_comparison.json").read_text(encoding="utf-8")
            )
            self.assertEqual(comparison["matched_case_count"], 1)
            self.assertEqual(comparison["deltas"]["governance_failure_count"], -1)
            matrix = (root / "reports" / "model_matrix.md").read_text(encoding="utf-8")
            self.assertIn("Governance Comparison (Tao-backed vs ungoverned)", matrix)

    def test_report_without_governance_mode_skips_comparison_artifact(self) -> None:
        score = base_score(case_id="case-1", driver="direct")
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            write_manifest(root)
            score_path = root / "score.json"
            score_path.write_text(json.dumps(score), encoding="utf-8")
            with mock.patch.object(
                sys, "argv", ["report.py", str(score_path), "--bench-root", str(root)]
            ):
                self.assertEqual(report.main(), 0)
            self.assertFalse((root / "reports" / "governance_comparison.json").exists())


if __name__ == "__main__":
    unittest.main()
