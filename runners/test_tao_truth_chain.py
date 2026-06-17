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


def minimal_result(tao_truth_chain: dict | None = None) -> dict:
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
    if tao_truth_chain is not None:
        result["tao_truth_chain"] = tao_truth_chain
    return result


class TaoTruthChainTests(unittest.TestCase):
    def test_score_preserves_optional_tao_truth_chain(self) -> None:
        chain = {
            "subject_id": "tao:node:claim-1",
            "artifact_ids": ["tao:node:patch-1"],
            "fact_kind": "TestResult",
            "fact_id": "tao:fact:l1-1",
            "verifier_input_ids": ["tao:node:bench-1"],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            write_manifest(root)
            result_path = root / "result.json"
            score_path = root / "score.json"
            result_path.write_text(json.dumps(minimal_result(chain)), encoding="utf-8")

            with mock.patch.object(
                sys,
                "argv",
                ["score_case.py", str(result_path), "--bench-root", str(root), "--out", str(score_path)],
            ):
                self.assertEqual(score_case.main(), 0)

            score = json.loads(score_path.read_text(encoding="utf-8"))
            self.assertEqual(score["tao_truth_chain"], chain)

    def test_score_keeps_direct_results_without_tao_ids_compatible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            write_manifest(root)
            result_path = root / "result.json"
            score_path = root / "score.json"
            result_path.write_text(json.dumps(minimal_result()), encoding="utf-8")

            with mock.patch.object(
                sys,
                "argv",
                ["score_case.py", str(result_path), "--bench-root", str(root), "--out", str(score_path)],
            ):
                self.assertEqual(score_case.main(), 0)

            score = json.loads(score_path.read_text(encoding="utf-8"))
            self.assertIsNone(score["tao_truth_chain"])

    def test_report_preserves_tao_truth_chains_in_machine_outputs(self) -> None:
        chain = {"subject_id": "tao:node:claim-1", "artifact_ids": ["tao:node:patch-1"]}
        score = {
            **minimal_result(chain),
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
            "has_hidden_verifier": False,
            "has_mutation_verifier": False,
            "hidden_pass": True,
            "mutation_pass": True,
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            write_manifest(root)
            score_path = root / "score.json"
            score_path.write_text(json.dumps(score), encoding="utf-8")

            with mock.patch.object(
                sys,
                "argv",
                ["report.py", str(score_path), "--bench-root", str(root)],
            ):
                self.assertEqual(report.main(), 0)

            per_track = json.loads((root / "reports" / "per_track.json").read_text(encoding="utf-8"))
            model_key = "m [patch/holon-cli]"
            self.assertEqual(
                per_track[model_key]["python_tool_engineering"]["tao_truth_chains"],
                [{"case_id": "case-1", "track": "python_tool_engineering", "tao_truth_chain": chain}],
            )


if __name__ == "__main__":
    unittest.main()
