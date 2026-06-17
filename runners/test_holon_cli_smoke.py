from __future__ import annotations

import pathlib
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import run_model_case

STUB = pathlib.Path(__file__).resolve().parent / "holon_stub.py"


def write_shim(root: pathlib.Path) -> pathlib.Path:
    """An executable holon shim that execs the offline stub."""
    shim = root / "holon"
    shim.write_text(
        f'#!/bin/sh\nexec "{sys.executable}" "{STUB}" "$@"\n', encoding="utf-8"
    )
    shim.chmod(0o755)
    return shim


def make_args() -> types.SimpleNamespace:
    return types.SimpleNamespace(
        model="holon-smoke",
        endpoint="http://127.0.0.1:1/v1",
        protocol="artifact",
        holon_max_iterations=100,
        holon_skip_auto=False,
        holon_timeout_seconds=60.0,
        holon_auto_timeout_seconds=60.0,
    )


class HolonCliSmokeTest(unittest.TestCase):
    def test_driver_runs_offline_against_real_stub(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            fixture = root / "fixtures" / "sample"
            (fixture / "src").mkdir(parents=True)
            (fixture / "src" / "tool.py").write_text(
                "def run():\n    return 1\n", encoding="utf-8"
            )
            shim = write_shim(root)

            case = {
                "id": "sample-smoke-001",
                "fixture": "fixtures/sample",
                "solution_paths": ["src/tool.py"],
                "constraints": [],
                "allowed_paths": ["src/tool.py"],
                "forbidden_paths": [],
                "user_request": "add a harmless marker",
                "verifier": {},
            }
            env = {
                "HOLON_BIN": str(shim),
                "HOLON_STUB_TARGET": "src/tool.py",
                "HOLON_STUB_ANCHOR": "def run",
                "HOLON_STUB_MARKER": "# stub marker\n",
                "HOLON_STUB_GOVERNANCE": "1",
                "HOLON_STUB_CASE": "sample-smoke-001",
            }
            # The dummy endpoint is never contacted: the stub edits the workspace
            # so the driver returns before any direct-endpoint fallback.
            with mock.patch.dict(run_model_case.os.environ, env):
                artifact, metadata = run_model_case.run_holon_cli_driver(
                    root, case, make_args(), prompt="prompt", fallback_prompt="fallback"
                )

            self.assertIn("# stub marker", artifact)
            self.assertEqual(metadata["generation_path"], "holon_workflow")
            self.assertFalse(metadata["fallback_used"])
            self.assertTrue(metadata["workflow_attempted"])
            self.assertEqual(metadata["governance_level"], "whitebox_native")
            self.assertEqual(metadata["governance_mode"], "governed")
            self.assertEqual(
                [check["name"] for check in metadata["governance_checks"]],
                ["scope_guard", "verifier_gate"],
            )
            self.assertEqual(
                metadata["tao_truth_chain"]["subject_id"], "case::sample-smoke-001"
            )


class ReadHolonGovernanceTest(unittest.TestCase):
    def test_absent_governance_keeps_metadata_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            (root / ".holon").mkdir()
            (root / "home").mkdir()
            trace = run_model_case.collect_holon_trace(
                workspace=root,
                home_dir=root / "home",
                auto_stdout="",
                snapshot_roots=[root],
            )
            self.assertNotIn("governance_mode", trace)
            self.assertNotIn("governance_checks", trace)
            self.assertNotIn("tao_truth_chain", trace)

    def test_present_governance_is_surfaced(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            holon = root / ".holon"
            holon.mkdir()
            (root / "home").mkdir()
            (holon / "governance.json").write_text(
                run_model_case.json.dumps(
                    {
                        "governance_mode": "governed",
                        "governance_checks": [{"name": "scope_guard", "passed": True}],
                        "tao_truth_chain": {"subject_id": "case::x"},
                    }
                ),
                encoding="utf-8",
            )
            trace = run_model_case.collect_holon_trace(
                workspace=root,
                home_dir=root / "home",
                auto_stdout="",
                snapshot_roots=[root],
            )
            self.assertEqual(trace["governance_mode"], "governed")
            self.assertEqual(trace["governance_checks"][0]["name"], "scope_guard")
            self.assertEqual(trace["tao_truth_chain"]["subject_id"], "case::x")

    def test_malformed_governance_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            holon = root / ".holon"
            holon.mkdir()
            (holon / "governance.json").write_text("{ not json", encoding="utf-8")
            self.assertEqual(run_model_case.read_holon_governance([root]), {})

    def test_invalid_governance_mode_is_dropped(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            holon = root / ".holon"
            holon.mkdir()
            (holon / "governance.json").write_text(
                run_model_case.json.dumps({"governance_mode": "bogus"}),
                encoding="utf-8",
            )
            self.assertEqual(run_model_case.read_holon_governance([root]), {})


if __name__ == "__main__":
    unittest.main()
