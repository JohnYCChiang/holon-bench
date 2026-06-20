"""Witness-file config-surface coverage for process-control and network-egress.

The fs witness-file gate (the real Holon binary's mechanism: an on-disk
``HOLON_TAO_FS_WITNESS`` file gates the permission decision) is exercised for the
real binary by ``holon_real_fs_governance_smoke.py`` and rehearsed offline via the
``holon_stub`` shim, which reads the same file. This test extends that coverage to
**process-control** and **network-egress**: the single witness file gates fs,
process, and net alike, so a ``process.kill`` / ``net.send`` grant in the file must
drive the stub's governed admit/deny exactly as an fs grant does.

It is **safe and offline by construction**: the stub models the action (it never
signals or kills a real process, nor resolves a name, opens a socket, or sends a
byte), so the *admit* path here is harmless. The genuine compiled-binary admit
path — which would run a real ``kill`` / ``curl`` — is deliberately left to the
opt-in real-binary smoke; this test proves the *gate* through the real config
surface without ever running a real command.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

RUNNERS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RUNNERS))

import holon_witness
STUB = RUNNERS / "holon_stub.py"
CASE_ID = "smoke"


def run_stub(witness_path: pathlib.Path | None, op: str) -> dict:
    """Run the stub in a temp cwd under the witness file for `op`; return its
    `.holon/governance.json` (or an empty dict when none was written)."""
    with tempfile.TemporaryDirectory(prefix="holon-real-procnet-") as temp:
        cwd = pathlib.Path(temp)
        env = os.environ.copy()
        env["HOLON_STUB_CASE"] = CASE_ID
        # The matched op (HOLON_STUB_FS_EFFECT_OP doubles as the generic op the
        # witness file is resolved against) and the op the record names.
        env["HOLON_STUB_FS_EFFECT_OP"] = op
        if op.startswith("process."):
            env["HOLON_STUB_PROCESS_OP"] = op
        elif op.startswith("net."):
            env["HOLON_STUB_NET_OP"] = op
        # Real config surface only: never lean on the in-process models here.
        for key in (
            "HOLON_STUB_FS_WITNESS",
            "HOLON_STUB_PROCESS_WITNESS",
            "HOLON_STUB_NET_WITNESS",
            "HOLON_STUB_TARGET",
        ):
            env.pop(key, None)
        if witness_path is not None:
            env["HOLON_TAO_FS_WITNESS"] = str(witness_path)
        else:
            env.pop("HOLON_TAO_FS_WITNESS", None)

        completed = subprocess.run(
            [sys.executable, str(STUB)],
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"stub failed ({completed.returncode}):\n{completed.stderr}"
            )
        gov = cwd / ".holon" / "governance.json"
        return json.loads(gov.read_text(encoding="utf-8")) if gov.is_file() else {}


class WitnessFileGatesProcessAndNet(unittest.TestCase):
    # op -> the governance check name the gate records for that class.
    CASES = {
        "process.kill": ("process_permission", "Killed"),
        "net.send": ("network_permission", "Sent"),
    }

    def _witness(self, tmp: pathlib.Path, op: str, decision: str) -> pathlib.Path:
        outcome = self.CASES[op][1]
        if decision == "admit":
            row = holon_witness.grant(op, "admit", result_type=outcome)
        else:
            row = holon_witness.grant(op, "deny", reason=f"witness denies {op}")
        return holon_witness.write_witness(tmp / f"{op}_{decision}.json", [row])

    def test_admit_grant_admits_the_op(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            tmp = pathlib.Path(t)
            for op, (check_name, _outcome) in self.CASES.items():
                witness = self._witness(tmp, op, "admit")
                gov = run_stub(witness, op)
                self.assertEqual(gov.get("governance_mode"), "governed", op)
                checks = {c["name"]: c for c in gov.get("governance_checks") or []}
                self.assertIs(
                    checks.get(check_name, {}).get("passed"),
                    True,
                    f"{op} admit grant must pass the {check_name} check",
                )

    def test_deny_grant_denies_the_op(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            tmp = pathlib.Path(t)
            for op, (check_name, _outcome) in self.CASES.items():
                witness = self._witness(tmp, op, "deny")
                gov = run_stub(witness, op)
                self.assertEqual(gov.get("governance_mode"), "governed", op)
                checks = {c["name"]: c for c in gov.get("governance_checks") or []}
                self.assertIs(
                    checks.get(check_name, {}).get("passed"),
                    False,
                    f"{op} deny grant must fail the {check_name} check",
                )

    def test_missing_grant_fails_closed(self) -> None:
        # A well-formed file whose only grant targets a different op → the
        # requested op has no matching row → missing-grant deny (fail closed).
        with tempfile.TemporaryDirectory() as t:
            tmp = pathlib.Path(t)
            witness = holon_witness.write_witness(
                tmp / "other.json",
                [holon_witness.grant("fs.delete", "admit", result_type="Unit")],
            )
            for op, (check_name, _outcome) in self.CASES.items():
                gov = run_stub(witness, op)
                checks = {c["name"]: c for c in gov.get("governance_checks") or []}
                self.assertIs(
                    checks.get(check_name, {}).get("passed"),
                    False,
                    f"{op} with no matching grant must fail closed",
                )

    def test_unconfigured_is_not_governed(self) -> None:
        # No witness file → the real config surface is unset → the stub falls
        # through to its in-process paths, which (with none set) are ungoverned.
        for op in self.CASES:
            gov = run_stub(None, op)
            self.assertNotEqual(
                gov.get("governance_mode"),
                "governed",
                f"{op} with no witness file must not be governed",
            )


if __name__ == "__main__":
    unittest.main()
