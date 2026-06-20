#!/usr/bin/env python3
"""Offline governed-vs-ungoverned smoke for the Holon process-control gate (M13c).

The process-control sibling of ``holon_fs_governance_smoke.py``. Where that smoke
gates an fs write, this one gates a *modeled* process-control action. Tao/Holon
landed the process-control EffectOps ``process.inspect | process.spawn |
process.signal | process.kill`` and Holon gates selected process-control actions
narrow-only. The domain claim is the *liveness/ownership* of running processes,
not filesystem write/read exposure.

The gated action is **modeled only** and harmless: this smoke never runs ``kill`` /
``pkill`` / ``killall`` / ``ps`` / ``pgrep`` or any command that signals, inspects,
spawns, or restarts a live process, and it never touches ``zhenren_bridge``. The
offline ``holon_stub`` models the witness decision under
``HOLON_STUB_PROCESS_WITNESS`` and records the modeled action as an inert marker. A
governed deny preserves process liveness/ownership and records a failing
``process_permission`` check, surfacing the governed-minus-ungoverned ``+1``
governance-failure delta over one matched case.

The shared three-scenario experiment lives in ``governance_smoke_harness``; this
slice supplies only the process-control parameters.
"""
from __future__ import annotations

from governance_smoke_harness import GovernanceSmokeSpec, run_governance_smoke

SPEC = GovernanceSmokeSpec(
    smoke_name="holon_process_governance_smoke",
    witness_env="HOLON_STUB_PROCESS_WITNESS",
    check_name="process_permission",
    marker="# holon process-witness smoke marker: modeled process.kill action via stub.\n",
    model_prefix="holon-process",
    temp_prefix="holon-bench-process-smoke-",
    summary_clause=(
        "ungoverned allow vs governed admit/deny modeled process control, no "
        "remote APIs and no real process touched"
    ),
    delta_label="process",
    deny_detail_phrase="liveness/ownership preserved",
    extra_env=(("HOLON_STUB_PROCESS_OP", "process.kill"),),
)


if __name__ == "__main__":
    raise SystemExit(run_governance_smoke(SPEC))
