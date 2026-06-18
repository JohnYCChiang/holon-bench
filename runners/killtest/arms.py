"""Arm drivers + per-command instrumentation.

The harness does not *play* the agent — Claude Code drives each run. The harness
provides the scaffold the agent acts inside and instruments every command so that
token accounting (M1/M2), edit counts, and verifier round-trips (M4) are derived
from the log, never from agent self-report (task req 8, prereg §3).

An ``ArmSession`` is the per-run instrument. Because the live agent invokes the
wrapper once per command (separate processes), session state (the token ledger,
counters, the open edit cycle) is persisted to ``<run_dir>/session.json`` and
reloaded on each ``wrap`` call. Edit-cycle boundaries: an *edit* command (Tao
``txn`` / a baseline file write) closes the previous cycle and opens a new one;
*verifier* and *context* commands attach to the current open cycle.
"""

from __future__ import annotations

import dataclasses
import datetime
import json
import pathlib
import subprocess
from dataclasses import dataclass, field
from typing import Any

from . import config
from .runlog import RunLog, RunHeader
from .tokens import TokenLedger, EditCycle, CAT_CONTEXT, CAT_DIAGNOSTIC


def now_ts() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# command classification ------------------------------------------------------

# Tao subcommands that are *edits* (open a new cycle).
TAO_EDIT = {"txn"}
# Tao subcommands that produce structured diagnostics / test results.
TAO_VERIFIER = {"check", "test", "law", "discharge"}
# Tao subcommands that place context into the window.
TAO_CONTEXT = {"ctx"}

# exit codes per tao-port/main.rs: 0 ok, 2 rejected/diagnostic, 3 test-not-passed.
TAO_DIAG_EXITS = {2, 3}


def classify_tao(argv: list[str]) -> str:
    sub = argv[0] if argv else ""
    if sub in TAO_EDIT:
        return "edit"
    if sub in TAO_VERIFIER:
        return "verifier"
    if sub in TAO_CONTEXT:
        return "context"
    return "query"


@dataclass
class CommandResult:
    argv: list[str]
    exit_code: int
    stdout: str
    stderr: str
    category: str
    accepted: bool
    is_diagnostic: bool


@dataclass
class ArmSession:
    run_dir: pathlib.Path
    header: RunHeader
    ledger: TokenLedger = field(default_factory=TokenLedger)
    edits_submitted: int = 0
    edits_accepted: int = 0
    #: scoring runs commands through the same session but must not count them
    #: as agent activity (P6 shakedown finding — M3/M9 contamination).
    recording: bool = True
    roundtrips: int = 0
    recoveries: int = 0
    _last_edit_failed: bool = False
    _open_cycle_index: int | None = None

    # persistence --------------------------------------------------------------

    @property
    def session_path(self) -> pathlib.Path:
        return self.run_dir / "session.json"

    @property
    def log(self) -> RunLog:
        return RunLog(self.run_dir / "run.jsonl")

    def save(self) -> None:
        data = {
            "header": self.header.to_dict(),
            "ledger": _ledger_to_json(self.ledger),
            "edits_submitted": self.edits_submitted,
            "edits_accepted": self.edits_accepted,
            "roundtrips": self.roundtrips,
            "recoveries": self.recoveries,
            "_last_edit_failed": self._last_edit_failed,
            "_open_cycle_index": self._open_cycle_index,
        }
        self.session_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    @classmethod
    def load(cls, run_dir: pathlib.Path) -> "ArmSession":
        path = pathlib.Path(run_dir) / "session.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        header = RunHeader(
            run_id=data["header"]["run_id"], arm=data["header"]["arm"],
            model_id=data["header"]["model_id"],
            harness_version_hash=data["header"]["harness_version_hash"],
            toolchain_set_hash=data["header"]["toolchain_set_hash"],
            suite_hashes=data["header"]["suite_hashes"],
            decoy=data["header"].get("decoy", False),
        )
        s = cls(run_dir=pathlib.Path(run_dir), header=header)
        s.ledger = _ledger_from_json(data["ledger"])
        s.edits_submitted = data["edits_submitted"]
        s.edits_accepted = data["edits_accepted"]
        s.roundtrips = data["roundtrips"]
        s.recoveries = data["recoveries"]
        s._last_edit_failed = data["_last_edit_failed"]
        s._open_cycle_index = data["_open_cycle_index"]
        return s

    # lifecycle ----------------------------------------------------------------

    def set_standing(self, *docs: str) -> int:
        return self.ledger.set_standing(*docs, label="standing-context")

    def _current_cycle(self) -> EditCycle | None:
        if self._open_cycle_index is None:
            return None
        return self.ledger.cycles[self._open_cycle_index]

    def _close_open_cycle(self) -> None:
        cyc = self._current_cycle()
        if cyc is not None:
            self.log.cycle(self.header.run_id, self.header.arm, cyc.to_dict(), now_ts())
        self._open_cycle_index = None

    def finish(self, outcome: str, anomalies: list[str] | None = None) -> None:
        self._close_open_cycle()
        self.log.run_end(
            self.header.run_id, self.header.arm, outcome=outcome,
            edits_submitted=self.edits_submitted, edits_accepted=self.edits_accepted,
            roundtrips=self.roundtrips, anomalies=anomalies or [], ts=now_ts())
        self.save()

    # the accounting core ------------------------------------------------------

    def record(self, argv: list[str], *, exit_code: int, stdout: str, stderr: str,
               category: str, accepted: bool, is_diagnostic: bool) -> None:
        """Account one command into the token ledger + run log."""
        if not self.recording:
            return
        label = " ".join(argv[:2]) if argv else category
        if category == "edit":
            self._close_open_cycle()
            cyc = self.ledger.open_cycle("txn" if argv[:1] == ["txn"] else "file_write")
            self._open_cycle_index = cyc.index
            cyc.accepted = accepted
            self.edits_submitted += 1
            if accepted:
                self.edits_accepted += 1
                if self._last_edit_failed:
                    # a rejected edit followed by a successful retry (M9).
                    self.recoveries += 1
            self._last_edit_failed = not accepted
            # the diagnostic the agent reads back from its own edit attempt.
            cyc.add(CAT_DIAGNOSTIC if is_diagnostic else CAT_CONTEXT,
                    f"edit:{label}", stdout + stderr)
            if is_diagnostic:
                self.roundtrips += 1
                self.log.roundtrip(self.header.run_id, self.header.arm,
                                   kind="edit-rejected", detail=label, ts=now_ts())
            return

        cyc = self._current_cycle()
        if cyc is None:
            # context/verifier before any edit: open an implicit read-only cycle.
            cyc = self.ledger.open_cycle("read")
            self._open_cycle_index = cyc.index
        cat = CAT_CONTEXT if category == "context" else CAT_DIAGNOSTIC
        cyc.add(cat, f"{category}:{label}", stdout + stderr)
        if is_diagnostic:
            self.roundtrips += 1
            self.log.roundtrip(self.header.run_id, self.header.arm,
                               kind=category, detail=label, ts=now_ts())

    # live tao-port instrumentation -------------------------------------------

    def run_tao(self, paths: config.Paths, store: pathlib.Path, argv: list[str],
                stdin_text: str | None = None) -> CommandResult:
        cmd = [str(paths.tao_port), argv[0], "--store", str(store), *argv[1:]]
        proc = subprocess.run(cmd, input=stdin_text, text=True, capture_output=True, check=False)
        category = classify_tao(argv)
        is_diag = proc.returncode in TAO_DIAG_EXITS and category in ("edit", "verifier")
        accepted = (category == "edit" and proc.returncode == 0)
        self.record(argv, exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr,
                    category=category, accepted=accepted, is_diagnostic=is_diag)
        return CommandResult(argv, proc.returncode, proc.stdout, proc.stderr,
                             category, accepted, is_diag)

    # baseline (git/cargo/file) instrumentation -------------------------------

    def run_baseline(self, workdir: pathlib.Path, command: str, *,
                     category: str) -> CommandResult:
        proc = subprocess.run(command, cwd=str(workdir), shell=True, text=True,
                              capture_output=True, check=False)
        is_diag = (category == "verifier" and proc.returncode != 0)
        accepted = (category == "edit" and proc.returncode == 0)
        argv = command.split()
        self.record(argv, exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr,
                    category=category, accepted=accepted, is_diagnostic=is_diag)
        return CommandResult(argv, proc.returncode, proc.stdout, proc.stderr,
                             category, accepted, is_diag)

    def record_file_write(self, rel_path: str, content: str) -> None:
        """A baseline file edit: the written content is what enters context."""
        self.record(["file_write", rel_path], exit_code=0, stdout=content, stderr="",
                    category="edit", accepted=True, is_diagnostic=False)


# ledger (de)serialisation ----------------------------------------------------

def _ledger_to_json(ledger: TokenLedger) -> dict[str, Any]:
    return {
        "standing_tokens": ledger.standing_tokens,
        "standing_label": ledger.standing_label,
        "cycles": [
            {"index": c.index, "kind": c.kind, "accepted": c.accepted,
             "survived": c.survived,
             "entries": [dataclasses.asdict(e) for e in c.entries]}
            for c in ledger.cycles
        ],
    }


def _ledger_from_json(data: dict[str, Any]) -> TokenLedger:
    from .tokens import LedgerEntry
    led = TokenLedger(standing_tokens=data["standing_tokens"],
                      standing_label=data.get("standing_label", "standing-context"))
    for c in data["cycles"]:
        cyc = EditCycle(index=c["index"], kind=c["kind"], accepted=c["accepted"],
                        survived=c.get("survived", True))
        for e in c["entries"]:
            cyc.entries.append(LedgerEntry(category=e["category"], label=e["label"],
                                           tokens=e["tokens"],
                                           observational=e.get("observational", {})))
        led.cycles.append(cyc)
    return led
