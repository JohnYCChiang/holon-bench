"""Pre-run checklist gate (spike plan P5 / prereg §7).

The real experiment (P5 shakedown → P6 runs) must not start until every frozen
pre-run surface is satisfied AND the Legislator confirms. This module computes
the gate mechanically from the experiment record + repo state; it never flips the
Legislator-confirm bit itself (that is a human act, recorded as a sentinel file).

Checklist items (spike plan P5 pre-run list + prereg §5/§7):
  1. suite hashes committed to the run log (G3 witness)
  2. harness version hash recorded
  3. exact model ID recorded (claude-fable-5 line, prereg §7)
  4. N=5 per arm confirmed, both arms
  5. hidden-suite leak scan clean (M10 not pre-voided)
  6. trusted-toolchain registry present + SIGNED (G5a)
  7. Legislator confirmation present (sentinel)
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass
from typing import Any

from . import config
from .runlog import RunLog, EV_SUITE_COMMIT, EV_EXPERIMENT


CONFIRM_SENTINEL = "LEGISLATOR_CONFIRMED.json"


@dataclass
class CheckItem:
    key: str
    ok: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {"item": self.key, "ok": self.ok, "detail": self.detail}


def run_checklist(paths: config.Paths, experiment_log: pathlib.Path,
                  leak_clean: bool, *, n_per_arm: int = config.N_PER_ARM) -> dict[str, Any]:
    log = RunLog(experiment_log)
    records = log.read()
    commits = [r for r in records if r.get("event") == EV_SUITE_COMMIT]
    inits = [r for r in records if r.get("event") == EV_EXPERIMENT]

    items: list[CheckItem] = []

    # 1. suite hashes committed (G3).
    g3 = bool(commits and commits[0].get("suite_hashes"))
    items.append(CheckItem("g3_suite_hashes_committed", g3,
                           "suite_commit event with hashes present" if g3
                           else "no suite_commit (G3) event in run log"))

    # 2. harness version hash recorded.
    hv = bool(inits and inits[0].get("provenance", {}).get("harness_version_sha256"))
    items.append(CheckItem("harness_version_recorded", hv,
                           "harness_version_sha256 stamped" if hv
                           else "experiment_init missing harness version hash"))

    # 3. model id recorded + matches the pinned line.
    model_ok = bool(inits and inits[0].get("model_id", "").startswith(config.MODEL_ID_PINNED))
    items.append(CheckItem("model_id_recorded", model_ok,
                           f"model_id starts with {config.MODEL_ID_PINNED}" if model_ok
                           else f"model_id absent or not pinned to {config.MODEL_ID_PINNED}"))

    # 4. N per arm declared.
    params = inits[0].get("params", {}) if inits else {}
    n_ok = params.get("n_per_arm") == n_per_arm
    items.append(CheckItem("n_per_arm_confirmed", n_ok,
                           f"n_per_arm={n_per_arm} both arms" if n_ok
                           else f"n_per_arm not recorded as {n_per_arm}"))

    # 5. leak scan clean.
    items.append(CheckItem("hidden_leak_scan_clean", leak_clean,
                           "no hidden-suite fingerprints in arm-visible surfaces" if leak_clean
                           else "LEAK DETECTED — M10 void, INCONCLUSIVE"))

    # 6. registry present + SIGNED.
    reg_ok = False
    reg_detail = "registry file missing"
    if paths.registry.exists():
        reg = json.loads(paths.registry.read_text(encoding="utf-8"))
        tools = reg.get("tools", {})
        reg_ok = bool(tools) and all(t.get("status") == "SIGNED" for t in tools.values())
        reg_detail = ("all tool_versions SIGNED (G5a)" if reg_ok
                      else "registry present but not all tools SIGNED")
    items.append(CheckItem("trusted_toolchain_signed", reg_ok, reg_detail))

    # 7. Legislator confirmation sentinel.
    sentinel = experiment_log.parent / CONFIRM_SENTINEL
    confirmed = sentinel.exists()
    items.append(CheckItem("legislator_confirmed", confirmed,
                           f"{CONFIRM_SENTINEL} present" if confirmed
                           else f"awaiting Legislator confirmation ({CONFIRM_SENTINEL})"))

    gate_pass = all(i.ok for i in items)
    return {"gate_pass": gate_pass, "items": [i.to_dict() for i in items]}
