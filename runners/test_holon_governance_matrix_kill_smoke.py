"""Offline tests for the governance-matrix kill-readiness smoke (M16).

The fast tests assert each preregistered mutant still applies cleanly to its
pristine target (no source drift) and that both fault classes are represented --
no subprocess, remote API, or live process. One heavier end-to-end test stages a
throwaway root and confirms the harness can both establish a passing baseline and
kill a representative mutant; it re-drives the real matrix (which re-drives the
offline smokes) and stays entirely offline.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import holon_governance_matrix_kill_smoke as kill
from common import bench_root

REAL_ROOT = bench_root(".")


class MutantRegistryTest(unittest.TestCase):
    """The mutant set is well-formed and covers both fault classes."""

    def test_each_mutant_old_present_exactly_once(self) -> None:
        for mutant in kill.MUTANTS:
            text = (REAL_ROOT / mutant.target).read_text(encoding="utf-8")
            self.assertEqual(
                text.count(mutant.old),
                1,
                f"mutant {mutant.id!r} old fragment must appear exactly once in "
                f"{mutant.target} (got {text.count(mutant.old)}); source drift",
            )

    def test_mutant_changes_the_source(self) -> None:
        for mutant in kill.MUTANTS:
            self.assertNotEqual(mutant.old, mutant.new, mutant.id)

    def test_ids_unique(self) -> None:
        ids = [m.id for m in kill.MUTANTS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_both_fault_classes_present(self) -> None:
        targets = {m.target for m in kill.MUTANTS}
        # at least one aggregation fault (mutates the matrix itself) ...
        self.assertIn("runners/holon_governance_matrix.py", targets)
        # ... and at least one evidence fault (mutates the runtime).
        self.assertTrue(
            targets & {"runners/report.py", "runners/holon_stub.py"},
            "expected at least one runtime evidence-fault mutant",
        )


class HarnessEndToEndTest(unittest.TestCase):
    """Baseline passes; a representative mutant is killed. Offline, one stage each."""

    def test_baseline_matrix_passes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="matrix-kill-test-base-") as temp:
            temp_root = pathlib.Path(temp)
            kill.stage_root(REAL_ROOT, temp_root)
            completed = kill.run_matrix(temp_root)
        self.assertEqual(
            completed.returncode,
            0,
            f"pristine matrix must pass on a staged root.\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )

    def test_representative_mutant_is_killed(self) -> None:
        mutant = next(
            m for m in kill.MUTANTS if m.id == "agg-expected-delta-drift"
        )
        with tempfile.TemporaryDirectory(prefix="matrix-kill-test-mut-") as temp:
            temp_root = pathlib.Path(temp)
            kill.stage_root(REAL_ROOT, temp_root)
            kill.apply_mutant(temp_root, mutant)
            completed = kill.run_matrix(temp_root)
        self.assertNotEqual(
            completed.returncode,
            0,
            f"mutant {mutant.id!r} must make the matrix fail (be killed).\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
