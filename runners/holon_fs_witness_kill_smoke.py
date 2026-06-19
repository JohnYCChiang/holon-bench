#!/usr/bin/env python3
"""Offline kill-readiness smoke for the fs witness governance smokes.

The existing fs witness smokes -- ``holon_fs_governance_smoke.py`` (write) and
``holon_fs_read_governance_smoke.py`` (read) -- prove the *happy path*: governed
runs surface exactly the fs denial that the ungoverned baseline silently allowed.
A passing smoke alone, though, does not prove the smoke can *fail*: a smoke that
asserts nothing real would pass against a broken runtime just as happily.

This smoke applies offline counterfactual pressure. It stages a throwaway bench
root, injects a deliberate, preregistered regression into the governance
runtime, and reruns the relevant existing smoke against the mutated copy --
*requiring that smoke to fail*. A mutant the smoke fails to catch is a
**survivor**: evidence the smoke is weaker than it looks. Survivors exit nonzero
and are named (mutant id, target file, command that unexpectedly passed).

Scope / what this is NOT
------------------------
This is fs *witness governance* kill-readiness, exercised entirely offline
against the bench's own stub runtime. It is **not** the formal private Stage-1
Tao compression kill-test (``runners/run_killtest.py`` /
``docs/killtest-stage1-readiness.md`` /
``tao/docs/tao-killtest-prereg-v0.md``), which is a frozen, pre-registered,
arm-blind experiment over a private suite. The mutants here are public, textual,
and target only the bench's fs witness smoke surface.

Mechanics
---------
- Staging is copy-light: ``runners/`` is *copied* (so the mutant edits a throwaway
  file, never tracked source), and every other top-level entry of the bench root
  is *symlinked* read-only. Nothing under the real tree is mutated.
- Each mutant is a single deterministic find/replace whose ``old`` text must be
  present in the pristine source (drift fails loudly rather than silently
  no-op'ing into a false survivor).
- Before mutating, each distinct target smoke is run once *unmutated* against a
  staged root and is required to PASS. A failing baseline means the harness is
  broken; we abort rather than miscredit it as a kill.
- No network, model endpoint, or compiled Holon binary is used; the target
  smokes dial an unreachable endpoint that their governed/denied paths never
  contact, so the run is deterministic and offline.
"""
from __future__ import annotations

import dataclasses
import pathlib
import shutil
import subprocess
import sys
import tempfile

from common import bench_root


@dataclasses.dataclass(frozen=True)
class Mutant:
    """One preregistered regression and the smoke that must kill it."""

    id: str
    target: str  # bench-root-relative source file to mutate
    smoke: str  # bench-root-relative smoke that must fail under the mutant
    old: str  # pristine text fragment (must be present exactly once)
    new: str  # regressed replacement
    regression: str  # human-readable description of the injected fault


# Preregistered mutants. Each ``old`` is a verbatim fragment of the pristine
# source; if a fragment drifts the smoke fails loudly (see apply_mutant) rather
# than silently producing a false survivor.
MUTANTS: tuple[Mutant, ...] = (
    Mutant(
        id="read-deny-exposes-context",
        target="runners/holon_stub.py",
        smoke="runners/holon_fs_read_governance_smoke.py",
        old='        if fs_decision == "admit":\n',
        new='        if fs_decision == "admit" or fs_kind() == "read":\n',
        regression=(
            "fs-read deny still applies the change, so the gated read marker "
            "(context) leaks into the artifact even when the witness denied it"
        ),
    ),
    Mutant(
        id="read-default-effectop-wrong-tier",
        target="runners/holon_stub.py",
        smoke="runners/holon_fs_read_governance_smoke.py",
        old=(
            '    return "read" if os.environ.get("HOLON_STUB_FS_KIND", "")'
            '.strip().lower().startswith("read") else "write"\n'
        ),
        new='    return "write"\n',
        regression=(
            "the fs-read default EffectOp tier (fs.read/fs.list) is mis-mapped to "
            "the write tier (fs.edit), so the read governance record loses its "
            "fs_read_permission framing"
        ),
    ),
    Mutant(
        id="write-deny-still-edits",
        target="runners/holon_stub.py",
        smoke="runners/holon_fs_governance_smoke.py",
        old='        if fs_decision == "admit":\n',
        new='        if fs_decision == "admit" or fs_kind() == "write":\n',
        regression=(
            "fs-write deny still applies the marker/edit, so a denied write "
            "mutates the workspace anyway"
        ),
    ),
    Mutant(
        id="comparison-suppresses-failure-count",
        target="runners/report.py",
        smoke="runners/holon_fs_governance_smoke.py",
        old=(
            "    governance_failure_count = sum(int(item.get"
            '("governance_failure_count", 0) or 0) for item in scores)\n'
        ),
        new="    governance_failure_count = 0\n",
        regression=(
            "the governance comparison zeroes the governed governance-failure "
            "count, hiding the governed-vs-ungoverned denial delta"
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
            f"holon_fs_witness_kill_smoke: mutant {mutant.id!r} no longer applies: "
            f"its preregistered text is absent from {mutant.target} (source drift)"
        )
    path.write_text(text.replace(mutant.old, mutant.new, 1), encoding="utf-8")


def run_smoke(temp_root: pathlib.Path, smoke: str) -> subprocess.CompletedProcess[str]:
    """Run a staged smoke against the staged root; return the completed process."""
    return subprocess.run(
        [sys.executable, str(temp_root / smoke), str(temp_root)],
        cwd=temp_root,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    real_root = bench_root(sys.argv[1] if len(sys.argv) > 1 else ".")

    # 1) Baseline: every distinct target smoke must PASS unmutated against a
    #    staged root. A failing baseline means the staging/harness is broken --
    #    abort rather than miscredit a broken harness as a kill.
    for smoke in sorted({m.smoke for m in MUTANTS}):
        with tempfile.TemporaryDirectory(prefix="holon-bench-kill-base-") as temp:
            temp_root = pathlib.Path(temp)
            stage_root(real_root, temp_root)
            completed = run_smoke(temp_root, smoke)
        if completed.returncode != 0:
            print(
                "holon_fs_witness_kill_smoke: HARNESS BROKEN "
                f"(baseline {smoke} failed unmutated, rc={completed.returncode}); "
                "cannot distinguish a kill from a broken stage.\n"
                f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
                file=sys.stderr,
            )
            return 2

    # 2) Mutation pressure: each mutant must make its smoke FAIL (be killed).
    killed: list[str] = []
    survivors: list[tuple[Mutant, str]] = []
    for mutant in MUTANTS:
        with tempfile.TemporaryDirectory(prefix="holon-bench-kill-") as temp:
            temp_root = pathlib.Path(temp)
            stage_root(real_root, temp_root)
            apply_mutant(temp_root, mutant)
            completed = run_smoke(temp_root, mutant.smoke)
        command = f"python3 {mutant.smoke} ."
        if completed.returncode == 0:
            survivors.append((mutant, command))
        else:
            killed.append(mutant.id)

    if survivors:
        print(
            f"holon_fs_witness_kill_smoke: SURVIVOR(S) ({len(survivors)} of "
            f"{len(MUTANTS)} mutant(s) not killed)",
            file=sys.stderr,
        )
        for mutant, command in survivors:
            print(
                f"  - mutant {mutant.id!r} survived\n"
                f"      target file: {mutant.target}\n"
                f"      regression : {mutant.regression}\n"
                f"      command that unexpectedly passed: {command}",
                file=sys.stderr,
            )
        return 1

    print(
        "holon_fs_witness_kill_smoke: ok "
        f"(killed {len(killed)}/{len(MUTANTS)} fs witness regression mutants, "
        "offline; NOT the private Stage-1 Tao kill-test). Killed: "
        + ", ".join(killed)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
