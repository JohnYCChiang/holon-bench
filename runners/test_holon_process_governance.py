"""Governed-vs-ungoverned smoke for the Holon process-control gate (M13c).

The process-control sibling of ``test_holon_fs_governance.py``. Tao/Holon landed
the process-control EffectOps ``process.inspect | process.spawn | process.signal |
process.kill`` and Holon gates selected process-control actions narrow-only. The
domain claim is the *liveness/ownership* of running processes.

The gated action is **modeled only** and harmless: the offline ``holon_stub``
never runs ``kill`` / ``pkill`` / ``ps`` / ``pgrep`` or any command that signals,
inspects, spawns, or restarts a real process. It models the witness decision
under ``HOLON_STUB_PROCESS_WITNESS`` and drives it through the real
``run_holon_cli_driver`` path so the process-governance surfacing/metadata is
exercised exactly as it would be for a real governed run.

The behavioral difference under test (process liveness/ownership):

- ungoverned (no witness installed): baseline allow -> the modeled action is
  recorded.
- governed + admit: the witness grants the process EffectOp -> the modeled action
  is recorded.
- governed + deny (missing grant): the modeled action is blocked -> nothing
  recorded and a failing ``process_permission`` check is logged.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import holon_stub
import run_model_case

STUB = pathlib.Path(__file__).resolve().parent / "holon_stub.py"
MARKER = "# process-witness stub marker\n"


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
        model="holon-process-smoke",
        endpoint="http://127.0.0.1:1/v1",
        protocol="artifact",
        holon_max_iterations=100,
        holon_skip_auto=False,
        holon_timeout_seconds=60.0,
        holon_auto_timeout_seconds=60.0,
    )


def run_case(witness: str | None) -> tuple[str, dict]:
    """Run the process case through the real driver with the given witness config."""
    case_id = "process-witness-001"
    with tempfile.TemporaryDirectory() as temp:
        root = pathlib.Path(temp)
        fixture = root / "fixtures" / "process"
        (fixture / "src").mkdir(parents=True)
        (fixture / "src" / "supervisor.py").write_text(
            "def supervise():\n    return 1\n", encoding="utf-8"
        )
        shim = write_shim(root)

        case = {
            "id": case_id,
            "fixture": "fixtures/process",
            "solution_paths": ["src/supervisor.py"],
            "constraints": [],
            "allowed_paths": ["src/supervisor.py"],
            "forbidden_paths": [],
            "user_request": "perform a guarded process-control action",
            "verifier": {},
        }
        env = {
            "HOLON_BIN": str(shim),
            "HOLON_STUB_TARGET": "src/supervisor.py",
            "HOLON_STUB_ANCHOR": "def supervise",
            "HOLON_STUB_MARKER": MARKER,
            "HOLON_STUB_CASE": case_id,
            "HOLON_STUB_PROCESS_OP": "process.kill",
        }
        if witness is not None:
            env["HOLON_STUB_PROCESS_WITNESS"] = witness
        # The dummy endpoint is never contacted: on admit the stub records the
        # modeled action; on deny the workflow path returns the trace without
        # falling back to the direct endpoint. No real process is touched.
        with mock.patch.dict(run_model_case.os.environ, env, clear=False):
            return run_model_case.run_holon_cli_driver(
                root, case, make_args(), prompt="prompt", fallback_prompt="fallback"
            )


class ProcessWitnessDecisionTest(unittest.TestCase):
    def test_unset_is_not_process_mode(self) -> None:
        with mock.patch.dict(holon_stub.os.environ, {}, clear=True):
            self.assertEqual(holon_stub.process_witness_decision(), (None, None))

    def test_absent_witness_is_ungoverned_allow(self) -> None:
        for value in ("none", "absent", "", "legacy", "unconfigured"):
            with mock.patch.dict(
                holon_stub.os.environ,
                {"HOLON_STUB_PROCESS_WITNESS": value},
                clear=True,
            ):
                self.assertEqual(
                    holon_stub.process_witness_decision(),
                    ("ungoverned", "admit"),
                    value,
                )

    def test_admit_values(self) -> None:
        for value in ("admit", "allow", "grant", "GRANTED"):
            with mock.patch.dict(
                holon_stub.os.environ,
                {"HOLON_STUB_PROCESS_WITNESS": value},
                clear=True,
            ):
                self.assertEqual(
                    holon_stub.process_witness_decision(),
                    ("governed", "admit"),
                    value,
                )

    def test_deny_and_unknown_fail_closed(self) -> None:
        for value in ("deny", "missing", "missing_grant", "denied", "garbage"):
            with mock.patch.dict(
                holon_stub.os.environ,
                {"HOLON_STUB_PROCESS_WITNESS": value},
                clear=True,
            ):
                self.assertEqual(
                    holon_stub.process_witness_decision(),
                    ("governed", "deny"),
                    value,
                )

    def test_default_process_effect_op(self) -> None:
        with mock.patch.dict(holon_stub.os.environ, {}, clear=True):
            self.assertEqual(holon_stub.default_process_effect_op(), "process.kill")
        for value in ("process.inspect", "process.spawn", "process.signal"):
            with mock.patch.dict(
                holon_stub.os.environ, {"HOLON_STUB_PROCESS_OP": value}, clear=True
            ):
                self.assertEqual(holon_stub.default_process_effect_op(), value)
        # Unknown / non-process op falls back to the liveness action.
        with mock.patch.dict(
            holon_stub.os.environ, {"HOLON_STUB_PROCESS_OP": "rm -rf"}, clear=True
        ):
            self.assertEqual(holon_stub.default_process_effect_op(), "process.kill")


class ProcessGovernanceDriverTest(unittest.TestCase):
    def test_legacy_unconfigured_emits_no_governance(self) -> None:
        # Pure legacy path (no process-witness mode at all): baseline allow and
        # byte-for-byte unchanged metadata -- no governance keys surface.
        artifact, metadata = run_case(witness=None)
        self.assertIn(MARKER.strip(), artifact)
        self.assertEqual(metadata["generation_path"], "holon_workflow")
        self.assertNotIn("governance_mode", metadata)
        self.assertNotIn("governance_checks", metadata)
        self.assertNotIn("tao_truth_chain", metadata)

    def test_ungoverned_preserves_baseline_allow(self) -> None:
        # Witness source unconfigured -> ungoverned, but still baseline allow.
        artifact, metadata = run_case(witness="none")
        self.assertIn(MARKER.strip(), artifact)
        self.assertEqual(metadata["generation_path"], "holon_workflow")
        self.assertFalse(metadata["fallback_used"])
        self.assertEqual(metadata["governance_mode"], "ungoverned")
        self.assertEqual(metadata["governance_checks"], [])
        self.assertNotIn("tao_truth_chain", metadata)

    def test_governed_admit_allows_process_action(self) -> None:
        artifact, metadata = run_case(witness="admit")
        self.assertIn(MARKER.strip(), artifact)
        self.assertFalse(metadata["fallback_used"])
        self.assertEqual(metadata["governance_mode"], "governed")
        checks = {c["name"]: c for c in metadata["governance_checks"]}
        self.assertIn("process_permission", checks)
        self.assertTrue(checks["process_permission"]["passed"])
        self.assertIn("process.kill", checks["process_permission"]["detail"])
        self.assertEqual(
            metadata["tao_truth_chain"]["subject_id"], "case::process-witness-001"
        )

    def test_governed_deny_blocks_process_action(self) -> None:
        artifact, metadata = run_case(witness="deny")
        # Witness denied the process EffectOp -> the modeled action was blocked.
        self.assertNotIn(MARKER.strip(), artifact)
        self.assertFalse(metadata["fallback_used"])
        self.assertEqual(metadata["governance_mode"], "governed")
        checks = {c["name"]: c for c in metadata["governance_checks"]}
        self.assertIn("process_permission", checks)
        self.assertFalse(checks["process_permission"]["passed"])
        self.assertIn("missing grant", checks["process_permission"]["detail"])
        self.assertIn(
            "liveness/ownership preserved", checks["process_permission"]["detail"]
        )

    def test_governed_deny_differs_from_ungoverned(self) -> None:
        """The core comparison: same case, opposite process outcome by config."""
        ungoverned_artifact, ungoverned_meta = run_case(witness="none")
        denied_artifact, denied_meta = run_case(witness="deny")
        self.assertIn(MARKER.strip(), ungoverned_artifact)
        self.assertNotIn(MARKER.strip(), denied_artifact)
        self.assertEqual(ungoverned_meta["governance_mode"], "ungoverned")
        self.assertEqual(denied_meta["governance_mode"], "governed")

    def test_inspect_op_frames_check_with_chosen_op(self) -> None:
        # HOLON_STUB_PROCESS_OP frames the governance detail; the read-like
        # inspect op flows through the same shared admit/deny path.
        case_id = "process-inspect-001"
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            fixture = root / "fixtures" / "process"
            (fixture / "src").mkdir(parents=True)
            (fixture / "src" / "supervisor.py").write_text(
                "def supervise():\n    return 1\n", encoding="utf-8"
            )
            shim = write_shim(root)
            case = {
                "id": case_id,
                "fixture": "fixtures/process",
                "solution_paths": ["src/supervisor.py"],
                "constraints": [],
                "allowed_paths": ["src/supervisor.py"],
                "forbidden_paths": [],
                "user_request": "perform a guarded process inspect",
                "verifier": {},
            }
            env = {
                "HOLON_BIN": str(shim),
                "HOLON_STUB_TARGET": "src/supervisor.py",
                "HOLON_STUB_ANCHOR": "def supervise",
                "HOLON_STUB_MARKER": MARKER,
                "HOLON_STUB_CASE": case_id,
                "HOLON_STUB_PROCESS_OP": "process.inspect",
                "HOLON_STUB_PROCESS_WITNESS": "deny",
            }
            with mock.patch.dict(run_model_case.os.environ, env, clear=False):
                _, metadata = run_model_case.run_holon_cli_driver(
                    root, case, make_args(), prompt="p", fallback_prompt="f"
                )
        checks = {c["name"]: c for c in metadata["governance_checks"]}
        self.assertIn("process_permission", checks)
        self.assertIn("process.inspect", checks["process_permission"]["detail"])


class FsBackwardCompatTest(unittest.TestCase):
    def test_process_witness_does_not_disturb_fs_witness(self) -> None:
        # The fs witness model is independent: setting HOLON_STUB_FS_WITNESS still
        # resolves the fs gate even when the process var is also present, and the
        # process var alone leaves the fs gate inert.
        with mock.patch.dict(
            holon_stub.os.environ,
            {"HOLON_STUB_PROCESS_WITNESS": "deny"},
            clear=True,
        ):
            self.assertEqual(holon_stub.fs_witness_decision(), (None, None))
        with mock.patch.dict(
            holon_stub.os.environ,
            {"HOLON_STUB_FS_WITNESS": "admit"},
            clear=True,
        ):
            self.assertEqual(holon_stub.process_witness_decision(), (None, None))


if __name__ == "__main__":
    unittest.main()
