from __future__ import annotations

import pathlib
import json
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import run_model_case
from run_model_case import extract_artifact_blocks, generation_fixture_ignore, write_artifact_workflow
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

    def test_holon_cli_caps_agent_iterations_and_sets_llamacpp_key(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            fixture = root / "fixtures" / "sample"
            fixture.mkdir(parents=True)
            (fixture / "src").mkdir()
            (fixture / "src" / "tool.py").write_text("def run():\n    return 1\n", encoding="utf-8")
            fake_holon = root / "holon"
            fake_holon.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            fake_holon.chmod(0o755)

            captured: dict[str, object] = {}

            def fake_run_process_group(command, cwd, env, timeout):
                settings = json.loads((pathlib.Path(cwd) / ".holon" / "settings.json").read_text())
                workflow_path = pathlib.Path(command[command.index("--workflow") + 1])
                workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
                captured["max_iterations"] = settings["capabilities"]["maxIterations"]
                captured["llamacpp_api_key"] = env.get("LLAMACPP_API_KEY")
                captured["thinking_budget"] = workflow["states"][0]["thinking_budget"]
                captured["max_output_tokens"] = workflow["states"][0]["max_output_tokens"]
                return types.SimpleNamespace(
                    stdout="--- FILE: src/tool.py ---\ndef run():\n    return 2\n",
                    stderr="",
                    returncode=0,
                )

            case = {
                "id": "sample-001",
                "fixture": "fixtures/sample",
                "solution_paths": ["src/tool.py"],
                "constraints": [],
                "allowed_paths": ["src/tool.py"],
                "forbidden_paths": [],
                "user_request": "change return value",
                "verifier": {},
            }
            args = types.SimpleNamespace(
                model="local-model",
                endpoint="http://127.0.0.1:8086/v1",
                protocol="artifact",
                holon_max_iterations=100,
                holon_skip_auto=False,
                holon_timeout_seconds=890.0,
                holon_auto_timeout_seconds=75.0,
            )

            with mock.patch.dict(run_model_case.os.environ, {"HOLON_BIN": str(fake_holon)}), mock.patch(
                "run_model_case.run_process_group", side_effect=fake_run_process_group
            ):
                artifact, _metadata = run_model_case.run_holon_cli_driver(
                    root,
                    case,
                    args,
                    prompt="prompt",
                    fallback_prompt="fallback",
                )

            self.assertIn("return 2", artifact)
            self.assertEqual(captured["max_iterations"], 12)
            self.assertEqual(captured["llamacpp_api_key"], "dummy")
            self.assertEqual(captured["thinking_budget"], 768)
            self.assertEqual(captured["max_output_tokens"], 4096)

    def test_holon_cli_print_fallback_uses_short_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            fixture = root / "fixtures" / "sample"
            fixture.mkdir(parents=True)
            (fixture / "src").mkdir()
            (fixture / "src" / "tool.py").write_text("def run():\n    return 1\n", encoding="utf-8")
            fake_holon = root / "holon"
            fake_holon.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            fake_holon.chmod(0o755)
            captured: dict[str, object] = {}

            def fake_fallback(*_args, timeout):
                captured["timeout"] = timeout
                return "--- FILE: src/tool.py ---\ndef run():\n    return 3\n"

            case = {
                "id": "sample-002",
                "fixture": "fixtures/sample",
                "solution_paths": ["src/tool.py"],
                "constraints": [],
                "allowed_paths": ["src/tool.py"],
                "forbidden_paths": [],
                "user_request": "change return value",
                "verifier": {},
            }
            args = types.SimpleNamespace(
                model="local-model",
                endpoint="http://127.0.0.1:8086/v1",
                protocol="artifact",
                holon_max_iterations=100,
                holon_skip_auto=True,
                holon_timeout_seconds=890.0,
                holon_auto_timeout_seconds=75.0,
            )

            with mock.patch.dict(run_model_case.os.environ, {"HOLON_BIN": str(fake_holon)}), mock.patch(
                "run_model_case.run_holon_prompt_fallback", side_effect=fake_fallback
            ):
                artifact, _metadata = run_model_case.run_holon_cli_driver(
                    root,
                    case,
                    args,
                    prompt="prompt",
                    fallback_prompt="fallback",
                )

            self.assertIn("return 3", artifact)
            self.assertEqual(captured["timeout"], 75.0)

    def test_artifact_workflow_includes_repair_feedback(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = pathlib.Path(temp)
            (workspace / ".holon").mkdir()
            previous = workspace / "previous.txt"
            previous.write_text("--- FILE: src/tool.py ---\nold\n", encoding="utf-8")
            case = {
                "id": "sample-003",
                "language": "python",
                "solution_paths": ["src/tool.py"],
                "constraints": ["keep schema"],
                "allowed_paths": ["src/tool.py"],
                "forbidden_paths": ["src/other.py"],
                "protected_paths": [],
                "user_request": "fix bug",
            }
            args = types.SimpleNamespace(
                model="local-model",
                endpoint="http://127.0.0.1:8086/v1",
                previous_artifact=str(previous),
                feedback_error="hidden verifier says redact token",
            )

            workflow_path = write_artifact_workflow(workspace=workspace, case=case, args=args)
            workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
            instructions = workflow["states"][0]["instructions_override"]

            self.assertEqual(workflow["states"][0]["thinking_budget"], 768)
            self.assertEqual(workflow["states"][0]["max_output_tokens"], 4096)
            self.assertIn("PREVIOUS ATTEMPT ARTIFACT", instructions)
            self.assertIn("hidden verifier says redact token", instructions)

    def test_artifact_workflow_timeout_does_not_fall_back_to_other_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            fixture = root / "fixtures" / "sample"
            fixture.mkdir(parents=True)
            (fixture / "src").mkdir()
            (fixture / "src" / "tool.py").write_text("def run():\n    return 1\n", encoding="utf-8")
            fake_holon = root / "holon"
            fake_holon.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            fake_holon.chmod(0o755)

            def timeout_workflow(*_args, **_kwargs):
                raise subprocess.TimeoutExpired("holon workflow", 75, output="partial workflow output")

            case = {
                "id": "sample-004",
                "fixture": "fixtures/sample",
                "solution_paths": ["src/tool.py"],
                "constraints": [],
                "allowed_paths": ["src/tool.py"],
                "forbidden_paths": [],
                "user_request": "change return value",
                "verifier": {},
            }
            args = types.SimpleNamespace(
                model="local-model",
                endpoint="http://127.0.0.1:8086/v1",
                protocol="artifact",
                holon_max_iterations=100,
                holon_skip_auto=False,
                holon_timeout_seconds=170.0,
                holon_auto_timeout_seconds=75.0,
            )

            with mock.patch.dict(run_model_case.os.environ, {"HOLON_BIN": str(fake_holon)}), mock.patch(
                "run_model_case.run_process_group", side_effect=timeout_workflow
            ), mock.patch("run_model_case.run_holon_prompt_fallback") as fallback, mock.patch(
                "run_model_case.request_patch"
            ) as direct:
                artifact, _metadata = run_model_case.run_holon_cli_driver(
                    root,
                    case,
                    args,
                    prompt="prompt",
                    fallback_prompt="fallback",
                )

            self.assertEqual(artifact, "partial workflow output")
            fallback.assert_not_called()
            direct.assert_not_called()


if __name__ == "__main__":
    unittest.main()
