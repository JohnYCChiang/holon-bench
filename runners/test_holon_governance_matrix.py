"""Offline tests for the governance capability matrix runner (M14).

The matrix re-drives the three completed witness smokes and confirms each still
surfaces its expected governed-minus-ungoverned ``+1`` governance-failure delta
over one matched case. These tests stay offline and deterministic by injecting a
fake smoke runner (canned ``CompletedProcess`` objects) instead of re-running the
real smokes, so the matrix's aggregation and fail-closed logic is exercised
without any subprocess, remote API, or live process. The real runner is exercised
once separately in validation.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import holon_governance_matrix as matrix


def ok_stdout(smoke_name: str, delta: int = 1, matched: int = 1) -> str:
    return (
        f"{smoke_name}: ok (ungoverned allow vs governed admit/deny, no remote "
        f"APIs; governed-minus-ungoverned governance-failure delta "
        f"{delta:+d} over {matched} matched case)\n"
    )


def fake_runner(responses: dict[str, subprocess.CompletedProcess]):
    """Return a runner callable that maps a smoke filename to a canned result."""

    def runner(root: pathlib.Path, runner_name: str) -> subprocess.CompletedProcess:
        return responses[runner_name]

    return runner


def all_pass_responses() -> dict[str, subprocess.CompletedProcess]:
    responses = {}
    for row in matrix.ROWS:
        smoke_name = pathlib.Path(row["runner"]).stem
        responses[row["runner"]] = subprocess.CompletedProcess(
            ["holon"], returncode=0, stdout=ok_stdout(smoke_name), stderr=""
        )
    return responses


ROOT = pathlib.Path("/bench-root")


class MatrixRowsTest(unittest.TestCase):
    def test_rows_cover_three_capability_classes(self) -> None:
        caps = [row["capability"] for row in matrix.ROWS]
        self.assertEqual(caps, ["fs-write", "fs-read", "process-control"])

    def test_rows_point_at_existing_smokes(self) -> None:
        runners_dir = pathlib.Path(__file__).resolve().parent
        for row in matrix.ROWS:
            self.assertTrue(
                (runners_dir / row["runner"]).is_file(),
                f"missing smoke: {row['runner']}",
            )
            # Each row expects the same governed-minus-ungoverned evidence.
            self.assertEqual(row["expected_delta"], 1)
            self.assertEqual(row["expected_matched_cases"], 1)


class MatrixAggregationTest(unittest.TestCase):
    def test_all_rows_pass(self) -> None:
        result = matrix.build_matrix(ROOT, runner=fake_runner(all_pass_responses()))
        self.assertTrue(result["ok"])
        self.assertEqual(result["row_count"], 3)
        self.assertTrue(all(row["ok"] for row in result["rows"]))
        for row in result["rows"]:
            self.assertEqual(row["observed_delta"], 1)
            self.assertEqual(row["observed_matched_cases"], 1)
            self.assertEqual(row["failures"], [])

    def test_matrix_output_is_json_serializable(self) -> None:
        result = matrix.build_matrix(ROOT, runner=fake_runner(all_pass_responses()))
        encoded = json.dumps(result, sort_keys=True)
        self.assertIn("holon_governance_matrix", encoded)

    def test_human_render_marks_pass(self) -> None:
        result = matrix.build_matrix(ROOT, runner=fake_runner(all_pass_responses()))
        text = matrix.render_human(result)
        self.assertIn("PASS", text)
        self.assertIn("3/3 capability rows confirmed", text)
        self.assertNotIn("FAIL", text)


class FailClosedTest(unittest.TestCase):
    def _responses_with(self, runner_name: str, completed):
        responses = all_pass_responses()
        responses[runner_name] = completed
        return responses

    def test_nonzero_exit_fails_closed(self) -> None:
        target = matrix.ROWS[0]["runner"]
        smoke_name = pathlib.Path(target).stem
        responses = self._responses_with(
            target,
            subprocess.CompletedProcess(
                ["holon"], returncode=1, stdout=f"{smoke_name}: boom\n", stderr="trace"
            ),
        )
        result = matrix.build_matrix(ROOT, runner=fake_runner(responses))
        self.assertFalse(result["ok"])
        failed = result["rows"][0]
        self.assertFalse(failed["ok"])
        self.assertEqual(failed["exit_code"], 1)
        self.assertTrue(any("non-clean" in f for f in failed["failures"]))
        # Diagnostics attached only on failure.
        self.assertIn("stderr_tail", failed)

    def test_wrong_delta_fails_closed(self) -> None:
        target = matrix.ROWS[1]["runner"]
        smoke_name = pathlib.Path(target).stem
        responses = self._responses_with(
            target,
            subprocess.CompletedProcess(
                ["holon"], returncode=0, stdout=ok_stdout(smoke_name, delta=2), stderr=""
            ),
        )
        result = matrix.build_matrix(ROOT, runner=fake_runner(responses))
        self.assertFalse(result["ok"])
        self.assertEqual(result["rows"][1]["observed_delta"], 2)
        self.assertTrue(
            any("delta" in f for f in result["rows"][1]["failures"])
        )

    def test_wrong_matched_case_count_fails_closed(self) -> None:
        target = matrix.ROWS[2]["runner"]
        smoke_name = pathlib.Path(target).stem
        responses = self._responses_with(
            target,
            subprocess.CompletedProcess(
                ["holon"], returncode=0, stdout=ok_stdout(smoke_name, matched=2), stderr=""
            ),
        )
        result = matrix.build_matrix(ROOT, runner=fake_runner(responses))
        self.assertFalse(result["ok"])
        self.assertTrue(
            any("matched-case" in f for f in result["rows"][2]["failures"])
        )

    def test_unparseable_output_fails_closed(self) -> None:
        target = matrix.ROWS[0]["runner"]
        responses = self._responses_with(
            target,
            subprocess.CompletedProcess(
                ["holon"], returncode=0, stdout="totally unrelated output\n", stderr=""
            ),
        )
        result = matrix.build_matrix(ROOT, runner=fake_runner(responses))
        self.assertFalse(result["ok"])
        failed = result["rows"][0]
        self.assertIsNone(failed["observed_delta"])
        self.assertTrue(any("parse" in f for f in failed["failures"]))
        self.assertTrue(any("report ok" in f for f in failed["failures"]))

    def test_missing_ok_token_fails_closed(self) -> None:
        # A summary line with the right delta but no "ok" status must not pass.
        target = matrix.ROWS[0]["runner"]
        smoke_name = pathlib.Path(target).stem
        responses = self._responses_with(
            target,
            subprocess.CompletedProcess(
                ["holon"],
                returncode=0,
                stdout=f"{smoke_name}: FAIL delta +1 over 1 matched case\n",
                stderr="",
            ),
        )
        result = matrix.build_matrix(ROOT, runner=fake_runner(responses))
        self.assertFalse(result["ok"])
        self.assertTrue(
            any("report ok" in f for f in result["rows"][0]["failures"])
        )

    def test_timeout_fails_closed(self) -> None:
        target = matrix.ROWS[0]["runner"]
        responses = self._responses_with(
            target,
            subprocess.CompletedProcess(
                ["holon"], returncode=None, stdout="", stderr="TIMEOUT after 600s"
            ),
        )
        result = matrix.build_matrix(ROOT, runner=fake_runner(responses))
        self.assertFalse(result["ok"])
        self.assertIsNone(result["rows"][0]["exit_code"])


class RunSmokeCommandTest(unittest.TestCase):
    def test_run_smoke_invokes_offline_runner(self) -> None:
        captured = {}

        def fake_subprocess_run(command, **kwargs):
            captured["command"] = command
            captured["kwargs"] = kwargs
            return subprocess.CompletedProcess(command, returncode=0, stdout="", stderr="")

        with mock.patch.object(matrix.subprocess, "run", fake_subprocess_run):
            matrix.run_smoke(ROOT, "holon_fs_governance_smoke.py")

        command = captured["command"]
        self.assertEqual(command[0], sys.executable)
        self.assertTrue(command[1].endswith("runners/holon_fs_governance_smoke.py"))
        self.assertEqual(command[2], str(ROOT))
        self.assertTrue(captured["kwargs"]["capture_output"])
        self.assertFalse(captured["kwargs"]["check"])
        # No shell: the command is an explicit argv list, never a shell string.
        self.assertIsInstance(command, list)


if __name__ == "__main__":
    unittest.main()
