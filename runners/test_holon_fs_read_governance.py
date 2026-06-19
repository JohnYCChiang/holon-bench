"""Governed-vs-ungoverned smoke for the Holon fs *read* permission path.

The read-side sibling of ``test_holon_fs_governance.py``. tao#18 adds the fs-read
tiers ``fs.stat | fs.list | fs.read`` and holon#11 maps ``read_file`` /
``grep_search`` to ``fs.read`` and ``glob_search`` to ``fs.list`` onto the same
``tao.fsWitness`` shape. The offline ``holon_stub`` models the witness decision
under ``HOLON_STUB_FS_KIND=read`` and drives it through the real
``run_holon_cli_driver`` path so the read-governance surfacing/metadata is
exercised exactly as it would be for a real governed run.

The behavioral difference under test (information boundary / context exposure):

- ungoverned (no witness installed): baseline allow -> the read is exposed.
- governed + admit: the witness grants fs.read/fs.list -> the read is exposed.
- governed + deny (missing grant): the context exposure is blocked -> no content
  surfaced and a failing ``fs_read_permission`` check is recorded.
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
MARKER = "# fs-read-witness stub marker\n"


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
        model="holon-fs-read-smoke",
        endpoint="http://127.0.0.1:1/v1",
        protocol="artifact",
        holon_max_iterations=100,
        holon_skip_auto=False,
        holon_timeout_seconds=60.0,
        holon_auto_timeout_seconds=60.0,
    )


def run_case(witness: str | None) -> tuple[str, dict]:
    """Run the fs-read case through the real driver with the given witness config."""
    case_id = "fs-read-witness-001"
    with tempfile.TemporaryDirectory() as temp:
        root = pathlib.Path(temp)
        fixture = root / "fixtures" / "fs"
        (fixture / "src").mkdir(parents=True)
        (fixture / "src" / "io.py").write_text(
            "def read():\n    return 1\n", encoding="utf-8"
        )
        shim = write_shim(root)

        case = {
            "id": case_id,
            "fixture": "fixtures/fs",
            "solution_paths": ["src/io.py"],
            "constraints": [],
            "allowed_paths": ["src/io.py"],
            "forbidden_paths": [],
            "user_request": "perform a guarded fs read",
            "verifier": {},
        }
        env = {
            "HOLON_BIN": str(shim),
            "HOLON_STUB_TARGET": "src/io.py",
            "HOLON_STUB_ANCHOR": "def read",
            "HOLON_STUB_MARKER": MARKER,
            "HOLON_STUB_CASE": case_id,
            "HOLON_STUB_FS_KIND": "read",
        }
        if witness is not None:
            env["HOLON_STUB_FS_WITNESS"] = witness
        # The dummy endpoint is never contacted: on admit the stub exposes the
        # read into the workspace artifact; on deny the workflow path returns the
        # trace without falling back to the direct endpoint.
        with mock.patch.dict(run_model_case.os.environ, env, clear=False):
            return run_model_case.run_holon_cli_driver(
                root, case, make_args(), prompt="prompt", fallback_prompt="fallback"
            )


class FsReadKindTest(unittest.TestCase):
    def test_default_effect_op_tracks_kind(self) -> None:
        with mock.patch.dict(holon_stub.os.environ, {}, clear=True):
            self.assertEqual(holon_stub.fs_kind(), "write")
            self.assertEqual(holon_stub.default_effect_op(), "fs.edit")
        with mock.patch.dict(
            holon_stub.os.environ, {"HOLON_STUB_FS_KIND": "read"}, clear=True
        ):
            self.assertEqual(holon_stub.fs_kind(), "read")
            self.assertEqual(holon_stub.default_effect_op(), "fs.read")

    def test_decision_logic_is_shared_with_write(self) -> None:
        # The admit/deny resolution itself is op-agnostic: kind only changes the
        # governance framing, not whether the witness admits or denies.
        for value, expected in (
            ("none", ("ungoverned", "admit")),
            ("admit", ("governed", "admit")),
            ("deny", ("governed", "deny")),
            ("garbage", ("governed", "deny")),
        ):
            with mock.patch.dict(
                holon_stub.os.environ,
                {"HOLON_STUB_FS_WITNESS": value, "HOLON_STUB_FS_KIND": "read"},
                clear=True,
            ):
                self.assertEqual(holon_stub.fs_witness_decision(), expected, value)


class FsReadGovernanceDriverTest(unittest.TestCase):
    def test_ungoverned_preserves_baseline_exposure(self) -> None:
        # Witness source unconfigured -> ungoverned, but still baseline allow:
        # the read is exposed and no governance failure surfaces.
        artifact, metadata = run_case(witness="none")
        self.assertIn(MARKER.strip(), artifact)
        self.assertEqual(metadata["generation_path"], "holon_workflow")
        self.assertFalse(metadata["fallback_used"])
        self.assertEqual(metadata["governance_mode"], "ungoverned")
        self.assertEqual(metadata["governance_checks"], [])
        self.assertNotIn("tao_truth_chain", metadata)

    def test_governed_admit_allows_fs_read(self) -> None:
        artifact, metadata = run_case(witness="admit")
        self.assertIn(MARKER.strip(), artifact)
        self.assertFalse(metadata["fallback_used"])
        self.assertEqual(metadata["governance_mode"], "governed")
        checks = {c["name"]: c for c in metadata["governance_checks"]}
        self.assertIn("fs_read_permission", checks)
        self.assertTrue(checks["fs_read_permission"]["passed"])
        self.assertIn("fs.read/fs.list", checks["fs_read_permission"]["detail"])
        self.assertEqual(
            metadata["tao_truth_chain"]["subject_id"], "case::fs-read-witness-001"
        )

    def test_governed_deny_blocks_context_exposure(self) -> None:
        artifact, metadata = run_case(witness="deny")
        # Witness denied the fs.read EffectOp -> the exposure was blocked offline.
        self.assertNotIn(MARKER.strip(), artifact)
        self.assertFalse(metadata["fallback_used"])
        self.assertEqual(metadata["governance_mode"], "governed")
        checks = {c["name"]: c for c in metadata["governance_checks"]}
        self.assertIn("fs_read_permission", checks)
        self.assertFalse(checks["fs_read_permission"]["passed"])
        self.assertIn("context exposure blocked", checks["fs_read_permission"]["detail"])

    def test_governed_deny_differs_from_ungoverned(self) -> None:
        """The core comparison: same case, opposite read outcome by config."""
        ungoverned_artifact, ungoverned_meta = run_case(witness="none")
        denied_artifact, denied_meta = run_case(witness="deny")
        self.assertIn(MARKER.strip(), ungoverned_artifact)
        self.assertNotIn(MARKER.strip(), denied_artifact)
        self.assertEqual(ungoverned_meta["governance_mode"], "ungoverned")
        self.assertEqual(denied_meta["governance_mode"], "governed")

    def test_write_kind_unaffected_records_fs_permission(self) -> None:
        # Backward-compat guard: without the read kind the gate still frames the
        # write check as ``fs_permission`` (the fs-write slice is untouched).
        case_id = "fs-write-witness-001"
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
                "HOLON_STUB_FS_WITNESS": "admit",
            }
            with mock.patch.dict(run_model_case.os.environ, env, clear=False):
                _, metadata = run_model_case.run_holon_cli_driver(
                    root, case, make_args(), prompt="p", fallback_prompt="f"
                )
        checks = {c["name"]: c for c in metadata["governance_checks"]}
        self.assertIn("fs_permission", checks)
        self.assertNotIn("fs_read_permission", checks)


if __name__ == "__main__":
    unittest.main()
