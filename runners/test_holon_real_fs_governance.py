"""Tests for the real-binary fs EffectOp witness path (holon#7 / 394a734).

Covers three things the real-binary smoke depends on, all runnable offline:

1. Witness file generation (``holon_witness``): the documented ``{ grants: [...] }``
   shape and the admit-needs-resultType / deny-needs-reason contract.
2. The stub's real config-surface gate (``HOLON_TAO_FS_WITNESS``): admit, missing
   grant, malformed file, unset, relative-path resolution, and env-over-model
   precedence over the legacy ``HOLON_STUB_FS_WITNESS`` model.
3. The smoke entrypoint's skip/no-binary behavior and its end-to-end run against
   the offline stub acting as a faithful real binary -- so the offline stub path
   stays intact while the real witness file path is exercised.
"""
from __future__ import annotations

import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import holon_real_fs_governance_smoke as real_smoke
import holon_stub
import holon_witness

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
STUB = pathlib.Path(__file__).resolve().parent / "holon_stub.py"


def write_shim(root: pathlib.Path) -> pathlib.Path:
    """A holon shim that execs the offline stub -- a faithful real-binary stand-in."""
    shim = root / "holon"
    shim.write_text(
        f'#!/bin/sh\nexec "{sys.executable}" "{STUB}" "$@"\n', encoding="utf-8"
    )
    shim.chmod(0o755)
    return shim


class WitnessBuilderTest(unittest.TestCase):
    def test_admit_grant_shape(self) -> None:
        grant = holon_witness.admit_grant("fs.edit", "src/io.py", result_type="Patch")
        self.assertEqual(grant["effectOp"], "fs.edit")
        self.assertEqual(grant["decision"], "admit")
        self.assertEqual(grant["resource"], "src/io.py")
        self.assertEqual(grant["resultType"], "Patch")

    def test_deny_grant_shape(self) -> None:
        grant = holon_witness.deny_grant("fs.edit", "src/io.py", reason="no grant")
        self.assertEqual(grant["decision"], "deny")
        self.assertEqual(grant["reason"], "no grant")

    def test_admit_requires_result_type(self) -> None:
        with self.assertRaises(holon_witness.WitnessError):
            holon_witness.grant("fs.edit", "admit", resource="x")

    def test_deny_requires_reason(self) -> None:
        with self.assertRaises(holon_witness.WitnessError):
            holon_witness.grant("fs.edit", "deny", resource="x")

    def test_unknown_effect_op_rejected(self) -> None:
        with self.assertRaises(holon_witness.WitnessError):
            holon_witness.grant("fs.touch", "admit", result_type="Patch")

    def test_unknown_decision_rejected(self) -> None:
        with self.assertRaises(holon_witness.WitnessError):
            holon_witness.grant("fs.edit", "maybe", result_type="Patch")

    def test_document_and_write_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = pathlib.Path(temp) / "w.json"
            grants = [holon_witness.admit_grant("fs.edit", "a", result_type="Patch")]
            holon_witness.write_witness(path, grants)
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data, {"grants": grants})

    def test_settings_snippet(self) -> None:
        snippet = holon_witness.settings_snippet(pathlib.Path("/tmp/w.json"))
        self.assertEqual(snippet["tao"]["fsWitness"]["path"], "/tmp/w.json")


class RealWitnessDecisionTest(unittest.TestCase):
    def _decide(self, env: dict, witness: dict | None) -> tuple:
        with tempfile.TemporaryDirectory() as temp:
            full_env = dict(env)
            if witness is not None:
                path = pathlib.Path(temp) / "witness.json"
                path.write_text(json.dumps(witness), encoding="utf-8")
                full_env["HOLON_TAO_FS_WITNESS"] = str(path)
            with mock.patch.dict(holon_stub.os.environ, full_env, clear=True):
                return holon_stub.real_witness_decision()

    def test_unset_is_not_real_mode(self) -> None:
        with mock.patch.dict(holon_stub.os.environ, {}, clear=True):
            self.assertEqual(holon_stub.real_witness_decision(), (None, None))

    def test_empty_is_not_real_mode(self) -> None:
        with mock.patch.dict(
            holon_stub.os.environ, {"HOLON_TAO_FS_WITNESS": "  "}, clear=True
        ):
            self.assertEqual(holon_stub.real_witness_decision(), (None, None))

    def test_matching_admit_grant(self) -> None:
        witness = {
            "grants": [
                holon_witness.admit_grant("fs.edit", "src/io.py", result_type="Patch")
            ]
        }
        decision = self._decide(
            {"HOLON_STUB_TARGET": "src/io.py", "HOLON_STUB_FS_EFFECT_OP": "fs.edit"},
            witness,
        )
        self.assertEqual(decision, ("governed", "admit"))

    def test_no_matching_row_is_missing_grant_deny(self) -> None:
        witness = {
            "grants": [
                holon_witness.admit_grant("fs.delete", "src/io.py", result_type="Unit")
            ]
        }
        decision = self._decide(
            {"HOLON_STUB_TARGET": "src/io.py", "HOLON_STUB_FS_EFFECT_OP": "fs.edit"},
            witness,
        )
        self.assertEqual(decision, ("governed", "deny"))

    def test_resource_mismatch_is_deny(self) -> None:
        witness = {
            "grants": [
                holon_witness.admit_grant("fs.edit", "other.py", result_type="Patch")
            ]
        }
        decision = self._decide(
            {"HOLON_STUB_TARGET": "src/io.py", "HOLON_STUB_FS_EFFECT_OP": "fs.edit"},
            witness,
        )
        self.assertEqual(decision, ("governed", "deny"))

    def test_explicit_deny_grant(self) -> None:
        witness = {
            "grants": [holon_witness.deny_grant("fs.edit", "src/io.py", reason="nope")]
        }
        decision = self._decide(
            {"HOLON_STUB_TARGET": "src/io.py", "HOLON_STUB_FS_EFFECT_OP": "fs.edit"},
            witness,
        )
        self.assertEqual(decision, ("governed", "deny"))

    def test_malformed_file_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = pathlib.Path(temp) / "bad.json"
            path.write_text("{ not json", encoding="utf-8")
            with mock.patch.dict(
                holon_stub.os.environ,
                {"HOLON_TAO_FS_WITNESS": str(path)},
                clear=True,
            ):
                self.assertEqual(
                    holon_stub.real_witness_decision(), ("governed", "deny")
                )

    def test_missing_file_fails_closed(self) -> None:
        with mock.patch.dict(
            holon_stub.os.environ,
            {"HOLON_TAO_FS_WITNESS": "/no/such/witness.json"},
            clear=True,
        ):
            self.assertEqual(holon_stub.real_witness_decision(), ("governed", "deny"))

    def test_grants_not_a_list_fails_closed(self) -> None:
        decision = self._decide(
            {"HOLON_STUB_TARGET": "src/io.py"}, {"grants": "nope"}
        )
        self.assertEqual(decision, ("governed", "deny"))

    def test_relative_path_resolves_against_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cwd = pathlib.Path(temp)
            (cwd / "rel.json").write_text(
                json.dumps(
                    {
                        "grants": [
                            holon_witness.admit_grant(
                                "fs.edit", "src/io.py", result_type="Patch"
                            )
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with mock.patch.object(holon_stub.pathlib.Path, "cwd", staticmethod(lambda: cwd)):
                with mock.patch.dict(
                    holon_stub.os.environ,
                    {
                        "HOLON_TAO_FS_WITNESS": "rel.json",
                        "HOLON_STUB_TARGET": "src/io.py",
                        "HOLON_STUB_FS_EFFECT_OP": "fs.edit",
                    },
                    clear=True,
                ):
                    self.assertEqual(
                        holon_stub.real_witness_decision(), ("governed", "admit")
                    )

    def test_real_witness_wins_over_stub_model(self) -> None:
        # env-over-model: HOLON_TAO_FS_WITNESS (deny) beats HOLON_STUB_FS_WITNESS=admit.
        witness = {
            "grants": [
                holon_witness.admit_grant("fs.delete", "src/io.py", result_type="Unit")
            ]
        }
        with tempfile.TemporaryDirectory() as temp:
            path = pathlib.Path(temp) / "w.json"
            path.write_text(json.dumps(witness), encoding="utf-8")
            env = {
                "HOLON_TAO_FS_WITNESS": str(path),
                "HOLON_STUB_FS_WITNESS": "admit",
                "HOLON_STUB_TARGET": "src/io.py",
                "HOLON_STUB_FS_EFFECT_OP": "fs.edit",
            }
            with mock.patch.dict(holon_stub.os.environ, env, clear=True):
                self.assertEqual(
                    holon_stub.real_witness_decision(), ("governed", "deny")
                )


class SmokeSkipTest(unittest.TestCase):
    def test_skips_cleanly_when_no_binary(self) -> None:
        out = io.StringIO()
        with mock.patch.dict(
            real_smoke.os.environ,
            {"HOLON_BIN": "/no/such/holon-binary"},
            clear=False,
        ):
            with mock.patch.object(sys, "argv", ["smoke", str(REPO_ROOT)]):
                with contextlib.redirect_stdout(out):
                    rc = real_smoke.main()
        self.assertEqual(rc, 0)
        self.assertIn("not-run", out.getvalue())

    def test_resolve_binary_accepts_executable(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            shim = write_shim(pathlib.Path(temp))
            with mock.patch.dict(
                real_smoke.os.environ, {"HOLON_BIN": str(shim)}, clear=False
            ):
                self.assertEqual(real_smoke.resolve_binary(), shim)

    def test_resolve_binary_rejects_non_executable(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            plain = pathlib.Path(temp) / "holon"
            plain.write_text("not executable", encoding="utf-8")
            plain.chmod(0o644)
            with mock.patch.dict(
                real_smoke.os.environ, {"HOLON_BIN": str(plain)}, clear=False
            ):
                self.assertIsNone(real_smoke.resolve_binary())


class SmokeEndToEndTest(unittest.TestCase):
    """Runs the full smoke against the offline stub as a faithful real binary."""

    def test_runs_against_stub_binary(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            shim = write_shim(pathlib.Path(temp))
            out = io.StringIO()
            env = {
                "HOLON_BIN": str(shim),
                "HOLON_SMOKE_ENDPOINT": real_smoke.DEFAULT_ENDPOINT,
            }
            # The dead endpoint is never contacted: the stub honors the witness
            # file deterministically, so no fallback to the endpoint occurs.
            with mock.patch.dict(real_smoke.os.environ, env, clear=False):
                with mock.patch.object(sys, "argv", ["smoke", str(REPO_ROOT)]):
                    with contextlib.redirect_stdout(out):
                        rc = real_smoke.main()
            self.assertEqual(rc, 0, out.getvalue())
            self.assertIn("ok", out.getvalue())


if __name__ == "__main__":
    unittest.main()
