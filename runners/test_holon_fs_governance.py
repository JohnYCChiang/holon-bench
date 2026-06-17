"""Governed-vs-ungoverned smoke for the one Holon fs permission path.

Holon#5 (merge e00cb8b) gates a single fs permission path through a Tao
``TaoEffectOpWitnessSource`` when one is installed, and preserves the legacy
behavior when it is not. The compiled Holon CLI does not yet expose an external
config surface for installing a witness source, so this bench models the witness
decision in the offline ``holon_stub`` (see
``.claude/tasks/holon-tao-witness-gate.md``) and drives it through the real
``run_holon_cli_driver`` path so the surfacing/metadata plumbing is exercised
exactly as it would be for a real governed run.

The behavioral difference under test:

- ungoverned (no witness installed): baseline allow -> the fs write happens.
- governed + admit: the witness grants the fs EffectOp -> the fs write happens.
- governed + deny (missing grant): the fs write is blocked -> no edit applied
  and a failing ``fs_permission`` check is recorded.
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
MARKER = "# fs-witness stub marker\n"


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
        model="holon-fs-smoke",
        endpoint="http://127.0.0.1:1/v1",
        protocol="artifact",
        holon_max_iterations=100,
        holon_skip_auto=False,
        holon_timeout_seconds=60.0,
        holon_auto_timeout_seconds=60.0,
    )


def run_case(witness: str | None) -> tuple[str, dict]:
    """Run the fs case through the real driver with the given witness config."""
    case_id = "fs-witness-001"
    with tempfile.TemporaryDirectory() as temp:
        root = pathlib.Path(temp)
        fixture = root / "fixtures" / "fs"
        (fixture / "src").mkdir(parents=True)
        (fixture / "src" / "io.py").write_text(
            "def write():\n    return 1\n", encoding="utf-8"
        )
        shim = write_shim(root)

        case = {
            "id": case_id,
            "fixture": "fixtures/fs",
            "solution_paths": ["src/io.py"],
            "constraints": [],
            "allowed_paths": ["src/io.py"],
            "forbidden_paths": [],
            "user_request": "perform a guarded fs write",
            "verifier": {},
        }
        env = {
            "HOLON_BIN": str(shim),
            "HOLON_STUB_TARGET": "src/io.py",
            "HOLON_STUB_ANCHOR": "def write",
            "HOLON_STUB_MARKER": MARKER,
            "HOLON_STUB_CASE": case_id,
        }
        if witness is not None:
            env["HOLON_STUB_FS_WITNESS"] = witness
        # The dummy endpoint is never contacted: on admit the stub edits the
        # workspace; on deny the workflow path returns the trace without falling
        # back to the direct endpoint.
        with mock.patch.dict(run_model_case.os.environ, env, clear=False):
            return run_model_case.run_holon_cli_driver(
                root, case, make_args(), prompt="prompt", fallback_prompt="fallback"
            )


class FsWitnessDecisionTest(unittest.TestCase):
    def test_unset_is_not_fs_mode(self) -> None:
        with mock.patch.dict(holon_stub.os.environ, {}, clear=True):
            self.assertEqual(holon_stub.fs_witness_decision(), (None, None))

    def test_absent_witness_is_ungoverned_allow(self) -> None:
        for value in ("none", "absent", "", "legacy", "unconfigured"):
            with mock.patch.dict(
                holon_stub.os.environ, {"HOLON_STUB_FS_WITNESS": value}, clear=True
            ):
                self.assertEqual(
                    holon_stub.fs_witness_decision(), ("ungoverned", "admit"), value
                )

    def test_admit_values(self) -> None:
        for value in ("admit", "allow", "grant", "GRANTED"):
            with mock.patch.dict(
                holon_stub.os.environ, {"HOLON_STUB_FS_WITNESS": value}, clear=True
            ):
                self.assertEqual(
                    holon_stub.fs_witness_decision(), ("governed", "admit"), value
                )

    def test_deny_and_unknown_fail_closed(self) -> None:
        for value in ("deny", "missing", "missing_grant", "denied", "garbage"):
            with mock.patch.dict(
                holon_stub.os.environ, {"HOLON_STUB_FS_WITNESS": value}, clear=True
            ):
                self.assertEqual(
                    holon_stub.fs_witness_decision(), ("governed", "deny"), value
                )


class FsGovernanceDriverTest(unittest.TestCase):
    def test_legacy_unconfigured_emits_no_governance(self) -> None:
        # Pure legacy path (no fs-witness mode at all): baseline allow and
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

    def test_governed_admit_allows_fs_write(self) -> None:
        artifact, metadata = run_case(witness="admit")
        self.assertIn(MARKER.strip(), artifact)
        self.assertFalse(metadata["fallback_used"])
        self.assertEqual(metadata["governance_mode"], "governed")
        checks = {c["name"]: c for c in metadata["governance_checks"]}
        self.assertIn("fs_permission", checks)
        self.assertTrue(checks["fs_permission"]["passed"])
        self.assertEqual(
            metadata["tao_truth_chain"]["subject_id"], "case::fs-witness-001"
        )

    def test_governed_deny_blocks_fs_write(self) -> None:
        artifact, metadata = run_case(witness="deny")
        # Witness denied the fs EffectOp -> the write was blocked offline.
        self.assertNotIn(MARKER.strip(), artifact)
        self.assertFalse(metadata["fallback_used"])
        self.assertEqual(metadata["governance_mode"], "governed")
        checks = {c["name"]: c for c in metadata["governance_checks"]}
        self.assertIn("fs_permission", checks)
        self.assertFalse(checks["fs_permission"]["passed"])
        self.assertIn("missing grant", checks["fs_permission"]["detail"])

    def test_governed_deny_differs_from_ungoverned(self) -> None:
        """The core comparison: same case, opposite fs outcome by config."""
        ungoverned_artifact, ungoverned_meta = run_case(witness="none")
        denied_artifact, denied_meta = run_case(witness="deny")
        self.assertIn(MARKER.strip(), ungoverned_artifact)
        self.assertNotIn(MARKER.strip(), denied_artifact)
        self.assertEqual(ungoverned_meta["governance_mode"], "ungoverned")
        self.assertEqual(denied_meta["governance_mode"], "governed")


if __name__ == "__main__":
    unittest.main()
