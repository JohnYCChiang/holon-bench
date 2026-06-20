#!/usr/bin/env python3
"""Offline kill-readiness smoke for the governance capability matrix (M16).

``holon_governance_matrix.py`` (M14/M15) aggregates the three completed
governed-vs-ungoverned witness smokes (fs-write, fs-read, process-control) into a
single fail-closed matrix and a stable ``governance-matrix/v1`` artifact. The
matrix's own tests prove it *passes* when the three smokes pass. A passing matrix
alone, though, does not prove the matrix can *fail*: a matrix whose checks were
vacuous -- or that silently stopped measuring real governance evidence -- would
pass just as happily against a broken runtime.

This smoke applies offline counterfactual pressure to the matrix itself. It stages
a throwaway bench root, injects a deliberate, preregistered regression, and reruns
the matrix against the mutated copy -- *requiring the matrix to fail*. A mutant the
matrix fails to catch is a **survivor**: evidence the matrix is weaker than it
looks. Survivors exit nonzero and are named (mutant id, target file, regression,
command that unexpectedly passed).

Two fault classes are exercised, both requiring the matrix to exit nonzero:

- **evidence faults** regress the underlying runtime (``report.py`` /
  ``holon_stub.py``) so a smoke's real governance evidence drops; the matrix must
  catch it end-to-end via that row's non-clean exit / delta mismatch. These include
  a *global* comparison mutant (all rows drop together) and one *per-row isolation*
  mutant for each of fs-write, fs-read, and process-control -- a regression confined
  to a single capability must fail the matrix via that capability's row alone.
- **aggregation faults** drift the matrix's *own* row metadata or summary parsing
  (``holon_governance_matrix.py``) so it would mis-measure even a correct, passing
  smoke; the matrix's present guard must fire.

Design boundary
---------------
Every mutant here injects a fault that is *observable against the real, passing
smokes*, so "require the matrix to fail" is the correct assertion. Guard-*vacuity*
mutants (e.g. deleting the delta comparison outright) produce no observable fault
against good smokes and would read as false survivors under this harness; that
failure mode is already covered by ``FailClosedTest`` in
``runners/test_holon_governance_matrix.py``, which injects a fake runner feeding bad
``CompletedProcess`` objects. This smoke is the end-to-end complement, not a
replacement.

Scope / what this is NOT
------------------------
This is governance-*matrix* kill-readiness, exercised entirely offline against the
bench's own stub runtime. It is **not** the formal private Stage-1 Tao compression
kill-test (``runners/run_killtest.py`` / ``tao/docs/tao-killtest-prereg-v0.md``),
which is a frozen, pre-registered, arm-blind experiment over a private suite. The
mutants here are public, textual, and target only the bench's matrix surface.

Safety: stub-only and offline. This smoke runs no live process-control command (no
``kill`` / ``pkill`` / ``killall`` / ``pgrep`` / ``ps`` / ``systemctl`` / ``jobs``)
and never inspects, attaches to, or interferes with any running service. It only
re-invokes the offline matrix, which itself only re-invokes the offline smokes.

Mechanics
---------
- Staging is copy-light: ``runners/`` is *copied* (so the mutant edits a throwaway
  file, never tracked source), and every other top-level entry of the bench root is
  *symlinked* read-only. Nothing under the real tree is mutated.
- Each mutant is a single deterministic find/replace whose ``old`` text must be
  present in the pristine source (drift fails loudly rather than silently no-op'ing
  into a false survivor).
- Before mutating, the pristine matrix is run once against a staged root and is
  required to PASS. A failing baseline means the harness is broken; we abort rather
  than miscredit it as a kill.
"""
from __future__ import annotations

import dataclasses
import pathlib
import shutil
import subprocess
import sys
import tempfile

from common import bench_root

# The matrix runner under counterfactual pressure; every mutant must make running
# this exit nonzero.
MATRIX = "runners/holon_governance_matrix.py"


@dataclasses.dataclass(frozen=True)
class Mutant:
    """One preregistered regression the matrix must fail under."""

    id: str
    target: str  # bench-root-relative source file to mutate
    old: str  # pristine text fragment (must be present exactly once)
    new: str  # regressed replacement
    regression: str  # human-readable description of the injected fault


# Preregistered mutants. Each ``old`` is a verbatim fragment of the pristine source;
# if a fragment drifts the smoke fails loudly (see apply_mutant) rather than
# silently producing a false survivor. The two ``expected_*`` aggregation mutants
# carry enough surrounding ROW context to locate a single, unambiguous row, since
# the bare ``"expected_delta": 1,`` / ``"expected_matched_cases": 1,`` lines repeat
# across the three rows.
MUTANTS: tuple[Mutant, ...] = (
    # --- evidence faults: regress the runtime; the matrix must catch it. ---
    Mutant(
        id="evidence-comparison-zeroes-failure-count",
        target="runners/report.py",
        old=(
            "    governance_failure_count = sum(int(item.get"
            '("governance_failure_count", 0) or 0) for item in scores)\n'
        ),
        new="    governance_failure_count = 0\n",
        regression=(
            "the governance comparison zeroes the governed governance-failure "
            "count, collapsing every smoke's governed-vs-ungoverned delta to +0; "
            "the matrix must reject the resulting delta mismatch"
        ),
    ),
    Mutant(
        id="evidence-write-deny-still-edits",
        target="runners/holon_stub.py",
        old='        if fs_decision == "admit":\n',
        new='        if fs_decision == "admit" or fs_kind() == "write":\n',
        regression=(
            "fs-write deny still applies the marker/edit, so the fs-write smoke "
            "stops surfacing its denial delta; the matrix's fs-write row must fail"
        ),
    ),
    # Per-row isolation: a regression confined to one capability must fail the
    # matrix *via that capability's row* while the other two rows still pass --
    # proving each row's fail-closed path is load-bearing on its own, not only
    # caught by the global comparison mutant above. (Isolation -- only the named
    # row failing -- is asserted in test_holon_governance_matrix_kill_smoke.py.)
    Mutant(
        id="evidence-read-deny-exposes-context",
        target="runners/holon_stub.py",
        old='        if fs_decision == "admit":\n',
        new='        if fs_decision == "admit" or fs_kind() == "read":\n',
        regression=(
            "fs-read deny still applies the change, so the gated read marker "
            "(context) leaks into the artifact even when the witness denied it; "
            "the matrix's fs-read row must fail while fs-write/process-control pass"
        ),
    ),
    Mutant(
        id="evidence-process-deny-records-pass",
        target="runners/holon_stub.py",
        old=(
            '                    "name": "process_permission",\n'
            '                    "passed": admitted,\n'
        ),
        new=(
            '                    "name": "process_permission",\n'
            '                    "passed": True,\n'
        ),
        regression=(
            "a denied modeled process-control action records its process_permission "
            "check as passed, hiding the governance failure; the matrix's "
            "process-control row must fail while fs-write/fs-read pass"
        ),
    ),
    # --- aggregation faults: drift the matrix's own metadata/parsing. ---
    Mutant(
        id="agg-expected-delta-drift",
        target="runners/holon_governance_matrix.py",
        old=(
            '        "capability": "fs-write",\n'
            '        "domain_claim": "protects filesystem mutation",\n'
            '        "runner": "holon_fs_governance_smoke.py",\n'
            '        "expected_delta": 1,\n'
        ),
        new=(
            '        "capability": "fs-write",\n'
            '        "domain_claim": "protects filesystem mutation",\n'
            '        "runner": "holon_fs_governance_smoke.py",\n'
            '        "expected_delta": 2,\n'
        ),
        regression=(
            "the fs-write row expects a +2 governance-failure delta the smoke never "
            "produces; the matrix's delta guard must fire on the real +1"
        ),
    ),
    Mutant(
        id="agg-matched-cases-drift",
        target="runners/holon_governance_matrix.py",
        old=(
            '        "capability": "fs-read",\n'
            '        "domain_claim": "protects context exposure / information '
            'boundary",\n'
            '        "runner": "holon_fs_read_governance_smoke.py",\n'
            '        "expected_delta": 1,\n'
            '        "expected_matched_cases": 1,\n'
        ),
        new=(
            '        "capability": "fs-read",\n'
            '        "domain_claim": "protects context exposure / information '
            'boundary",\n'
            '        "runner": "holon_fs_read_governance_smoke.py",\n'
            '        "expected_delta": 1,\n'
            '        "expected_matched_cases": 2,\n'
        ),
        regression=(
            "the fs-read row expects 2 matched cases where the smoke matches 1; the "
            "matrix's matched-case guard must fire"
        ),
    ),
    Mutant(
        id="agg-runner-path-wrong",
        target="runners/holon_governance_matrix.py",
        old='        "runner": "holon_process_governance_smoke.py",\n',
        new='        "runner": "holon_process_governance_smoke_MISSING.py",\n',
        regression=(
            "the process-control row points at a nonexistent runner; the matrix "
            "must fail closed when the smoke it claims to drive cannot be invoked"
        ),
    ),
    Mutant(
        id="agg-summary-regex-defanged",
        target="runners/holon_governance_matrix.py",
        old=(
            'SUMMARY_RE = re.compile(r"delta\\s+([+-]?\\d+)\\s+over\\s+(\\d+)'
            '\\s+matched case")\n'
        ),
        new=(
            "SUMMARY_RE = re.compile("
            'r"__never_matches_any_real_summary_line__([+-]?\\d+)\\s+(\\d+)")\n'
        ),
        regression=(
            "the matrix's summary parser can no longer match any smoke's evidence "
            "line, so every row loses its delta/matched-case reading; the matrix's "
            "fail-closed parse path must fire"
        ),
    ),
)


def stage_root(real_root: pathlib.Path, temp_root: pathlib.Path) -> None:
    """Stage a throwaway bench root: copy ``runners/``, symlink the rest.

    The mutant only ever edits the copied ``runners/`` tree, so tracked source is
    never touched. Everything else (manifest, cases, fixtures, schemas, ...) is
    symlinked read-only, keeping the stage cheap and offline.
    """
    for entry in sorted(real_root.iterdir()):
        if entry.name in (".git", "__pycache__"):
            continue
        dest = temp_root / entry.name
        if entry.name == "runners":
            shutil.copytree(
                entry, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
            )
        else:
            dest.symlink_to(entry.resolve())


def apply_mutant(temp_root: pathlib.Path, mutant: Mutant) -> None:
    """Apply a single deterministic find/replace to the staged copy."""
    path = temp_root / mutant.target
    text = path.read_text(encoding="utf-8")
    if mutant.old not in text:
        raise RuntimeError(
            f"holon_governance_matrix_kill_smoke: mutant {mutant.id!r} no longer "
            f"applies: its preregistered text is absent from {mutant.target} "
            "(source drift)"
        )
    path.write_text(text.replace(mutant.old, mutant.new, 1), encoding="utf-8")


def run_matrix(temp_root: pathlib.Path) -> subprocess.CompletedProcess[str]:
    """Run the staged matrix against the staged root; return the completed process."""
    return subprocess.run(
        [sys.executable, str(temp_root / MATRIX), str(temp_root)],
        cwd=temp_root,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    real_root = bench_root(sys.argv[1] if len(sys.argv) > 1 else ".")

    # 1) Baseline: the pristine matrix must PASS unmutated against a staged root. A
    #    failing baseline means the staging/harness is broken -- abort rather than
    #    miscredit a broken stage as a kill.
    with tempfile.TemporaryDirectory(prefix="holon-bench-matrix-kill-base-") as temp:
        temp_root = pathlib.Path(temp)
        stage_root(real_root, temp_root)
        baseline = run_matrix(temp_root)
    if baseline.returncode != 0:
        print(
            "holon_governance_matrix_kill_smoke: HARNESS BROKEN "
            f"(baseline matrix failed unmutated, rc={baseline.returncode}); "
            "cannot distinguish a kill from a broken stage.\n"
            f"stdout:\n{baseline.stdout}\nstderr:\n{baseline.stderr}",
            file=sys.stderr,
        )
        return 2

    # 2) Mutation pressure: each mutant must make the matrix FAIL (be killed).
    killed: list[str] = []
    survivors: list[Mutant] = []
    for mutant in MUTANTS:
        with tempfile.TemporaryDirectory(prefix="holon-bench-matrix-kill-") as temp:
            temp_root = pathlib.Path(temp)
            stage_root(real_root, temp_root)
            apply_mutant(temp_root, mutant)
            completed = run_matrix(temp_root)
        if completed.returncode == 0:
            survivors.append(mutant)
        else:
            killed.append(mutant.id)

    if survivors:
        print(
            f"holon_governance_matrix_kill_smoke: SURVIVOR(S) ({len(survivors)} of "
            f"{len(MUTANTS)} mutant(s) not killed)",
            file=sys.stderr,
        )
        for mutant in survivors:
            print(
                f"  - mutant {mutant.id!r} survived\n"
                f"      target file: {mutant.target}\n"
                f"      regression : {mutant.regression}\n"
                f"      command that unexpectedly passed: python3 {MATRIX} .",
                file=sys.stderr,
            )
        return 1

    print(
        "holon_governance_matrix_kill_smoke: ok "
        f"(killed {len(killed)}/{len(MUTANTS)} governance-matrix regression mutants, "
        "offline; NOT the private Stage-1 Tao kill-test). Killed: "
        + ", ".join(killed)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
