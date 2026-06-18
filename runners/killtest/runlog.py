"""Append-only JSONL run-log writer (spike plan Appendix A).

Appendix A minimal fields:
  run_id · arm · model_id · harness_version_hash · toolchain_set_hash ·
  suite_hashes (acceptance / hidden / per-arm renditions) · timestamps ·
  token ledger per edit cycle · edits (submitted / accepted) ·
  verifier round-trips · outcome · M5 minutes · anomalies

Discipline (prereg §5): all runs are reported, including crashed and abandoned
ones — no survivorship filtering. The log is strictly append-only: every event is
one JSON object on its own line; records are never rewritten in place. A crashed
run still ends with a terminal ``outcome`` event (outcome="crashed"/"abandoned").

Timestamps are passed in by the caller (the harness stamps wall-clock at the
boundary); this module never reads the clock itself, so it is replayable.
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field
from typing import Any


# event types written to the JSONL stream.
EV_EXPERIMENT = "experiment_init"   # provenance + pinned params (once, before run 1)
EV_SUITE_COMMIT = "suite_commit"    # G3 witness: all suite hashes before run 1
EV_RUN_START = "run_start"
EV_CYCLE = "edit_cycle"             # one token-accounted submit→diagnostics window
EV_ROUNDTRIP = "verifier_roundtrip"
EV_SCORE = "score"                  # acceptance/hidden/mutation results for a run
EV_REVIEW = "review"                # M5 minutes
EV_RUN_END = "run_end"             # terminal outcome (incl. crashed/abandoned)
EV_ANOMALY = "anomaly"
EV_CHECKLIST = "prerun_checklist"


# terminal outcomes (prereg §5: crashed/abandoned are first-class).
OUTCOMES = ("green", "failed", "crashed", "abandoned")


class RunLog:
    """Append-only JSONL sink. One instance per experiment record file."""

    def __init__(self, path: pathlib.Path):
        self.path = pathlib.Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: str, payload: dict[str, Any], *, ts: str | None = None) -> None:
        record = {"event": event}
        if ts is not None:
            record["ts"] = ts
        record.update(payload)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False))
            handle.write("\n")

    # convenience wrappers ------------------------------------------------------

    def experiment_init(self, *, model_id: str, provenance: dict[str, Any],
                        params: dict[str, Any], ts: str) -> None:
        self.append(EV_EXPERIMENT, {
            "model_id": model_id, "provenance": provenance, "params": params,
        }, ts=ts)

    def suite_commit(self, suite_hashes: dict[str, Any], *, witness: str, ts: str) -> None:
        # G3: the single outstanding pre-run act. Hidden suite is committed by
        # *hash only* — its contents never enter this log.
        self.append(EV_SUITE_COMMIT, {"suite_hashes": suite_hashes, "witness": witness}, ts=ts)

    def run_start(self, run: "RunHeader", ts: str) -> None:
        self.append(EV_RUN_START, run.to_dict(), ts=ts)

    def cycle(self, run_id: str, arm: str, cycle: dict[str, Any], ts: str) -> None:
        self.append(EV_CYCLE, {"run_id": run_id, "arm": arm, "cycle": cycle}, ts=ts)

    def roundtrip(self, run_id: str, arm: str, *, kind: str, detail: str, ts: str) -> None:
        # M4: counted from the log, not from agent self-report (task req 8).
        self.append(EV_ROUNDTRIP, {"run_id": run_id, "arm": arm, "kind": kind,
                                   "detail": detail}, ts=ts)

    def score(self, run_id: str, arm: str, score: dict[str, Any], ts: str) -> None:
        self.append(EV_SCORE, {"run_id": run_id, "arm": arm, "score": score}, ts=ts)

    def review(self, run_id: str, arm: str, *, minutes: float, reviewer: str,
               blind: bool, defects: list[dict[str, Any]] | None, ts: str) -> None:
        self.append(EV_REVIEW, {"run_id": run_id, "arm": arm, "minutes": minutes,
                                "reviewer": reviewer, "arm_blind": blind,
                                "defects": defects or []}, ts=ts)

    def run_end(self, run_id: str, arm: str, *, outcome: str, edits_submitted: int,
                edits_accepted: int, roundtrips: int, anomalies: list[str], ts: str) -> None:
        if outcome not in OUTCOMES:
            raise ValueError(f"unknown outcome {outcome!r}; expected one of {OUTCOMES}")
        self.append(EV_RUN_END, {
            "run_id": run_id, "arm": arm, "outcome": outcome,
            "edits_submitted": edits_submitted, "edits_accepted": edits_accepted,
            "verifier_roundtrips": roundtrips, "anomalies": anomalies,
        }, ts=ts)

    def anomaly(self, run_id: str, message: str, ts: str) -> None:
        self.append(EV_ANOMALY, {"run_id": run_id, "message": message}, ts=ts)

    def checklist(self, items: list[dict[str, Any]], *, gate_pass: bool, ts: str) -> None:
        self.append(EV_CHECKLIST, {"items": items, "gate_pass": gate_pass}, ts=ts)

    # reader --------------------------------------------------------------------

    def read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        out: list[dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                out.append(json.loads(line))
        return out

    def events(self, event: str) -> list[dict[str, Any]]:
        return [r for r in self.read() if r.get("event") == event]


@dataclass
class RunHeader:
    """The per-run identity stamped into ``run_start`` (Appendix A fields)."""

    run_id: str
    arm: str
    model_id: str
    harness_version_hash: str
    toolchain_set_hash: str
    suite_hashes: dict[str, Any]
    decoy: bool = False
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "arm": self.arm,
            "model_id": self.model_id,
            "harness_version_hash": self.harness_version_hash,
            "toolchain_set_hash": self.toolchain_set_hash,
            "suite_hashes": self.suite_hashes,
            "decoy": self.decoy,
            **self.extra,
        }
