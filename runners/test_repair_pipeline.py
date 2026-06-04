from __future__ import annotations

import pathlib
import json
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from run_model_case import extract_artifact_blocks, generation_fixture_ignore
from run_track import build_feedback_error, preserve_better_previous_attempt


class RepairPipelineTests(unittest.TestCase):
    def test_feedback_includes_hidden_mutation_and_semantic_failures(self) -> None:
        result = {
            "hard_gates": {"patch_applies": True, "schema_valid": True},
            "commands": [],
            "hidden_commands": [
                {
                    "command": "hidden-check",
                    "exit_code": 1,
                    "timed_out": False,
                    "stdout": "closed channel was not handled",
                    "stderr": "",
                }
            ],
            "mutation_commands": [
                {
                    "command": "mutation-check",
                    "exit_code": 1,
                    "timed_out": False,
                    "stdout": "zero workers deadlocked",
                    "stderr": "",
                }
            ],
            "semantic_checks": [
                {"name": "contract parity", "passed": False, "message": "schema drift"}
            ],
        }

        feedback = build_feedback_error({}, result)

        self.assertIn("Hidden Verifier failed", feedback)
        self.assertIn("closed channel was not handled", feedback)
        self.assertIn("Mutation Verifier failed", feedback)
        self.assertIn("zero workers deadlocked", feedback)
        self.assertIn("Semantic verifier failed", feedback)
        self.assertIn("schema drift", feedback)

    def test_extracts_xml_write_file_tool_call_as_artifact(self) -> None:
        output = """The fix is:
<tool_call>
<function=write_file>
<parameter=content>
package tick

func fixed() {}
</parameter>
<parameter=path>
server/tick/loop.go
</parameter>
</function>
</tool_call>
"""

        artifact = extract_artifact_blocks(output, ["server/tick/loop.go"])

        self.assertEqual(
            artifact,
            "--- FILE: server/tick/loop.go ---\npackage tick\n\nfunc fixed() {}\n",
        )

    def test_generation_workspace_excludes_hidden_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            source = root / "source"
            source.mkdir()
            (source / "visible.txt").write_text("visible", encoding="utf-8")
            (source / "hidden").mkdir()
            (source / "hidden" / "secret_test.py").write_text("secret", encoding="utf-8")
            destination = root / "destination"

            shutil.copytree(source, destination, ignore=generation_fixture_ignore)

            self.assertTrue((destination / "visible.txt").is_file())
            self.assertFalse((destination / "hidden").exists())

    def test_repair_cannot_replace_an_attempt_with_more_passing_gates(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            result = root / "model_case_result.json"
            artifact = root / "model_case_artifact.txt"
            previous_result = root / "model_case_attempt1_result.json"
            previous_artifact = root / "model_case_attempt1_artifact.txt"
            result.write_text(
                json.dumps({"hard_gates": {"tests_pass": True, "hidden_pass": False}}),
                encoding="utf-8",
            )
            artifact.write_text("worse", encoding="utf-8")
            previous_result.write_text(
                json.dumps({"hard_gates": {"tests_pass": True, "hidden_pass": True}}),
                encoding="utf-8",
            )
            previous_artifact.write_text("better", encoding="utf-8")

            reverted = preserve_better_previous_attempt(
                result_path=result,
                artifact_path=artifact,
                previous_result_path=previous_result,
                previous_artifact_path=previous_artifact,
                attempt_number=2,
            )

            restored = json.loads(result.read_text(encoding="utf-8"))
            self.assertTrue(reverted)
            self.assertTrue(restored["repair_reverted"])
            self.assertEqual(artifact.read_text(encoding="utf-8"), "better")
            self.assertTrue((root / "model_case_attempt2_rejected_result.json").is_file())


if __name__ == "__main__":
    unittest.main()
