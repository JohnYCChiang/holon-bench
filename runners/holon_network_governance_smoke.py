#!/usr/bin/env python3
"""Offline governed-vs-ungoverned smoke for the Holon network-egress gate (M19).

The network-egress sibling of ``holon_process_governance_smoke.py``. Where that
smoke gates a modeled process-control action, this one gates a *modeled*
network-egress action. Tao/Holon landed the network-egress EffectOps
``net.resolve | net.connect | net.send`` (tao#22) and Holon gates selected outbound
commands narrow-only. The domain claim is the *external-contact / exfiltration
boundary* (which external endpoints a context may reach and what it may send
outward), not filesystem write/read exposure or process liveness.

The gated action is **modeled only** and harmless: this smoke never runs ``curl`` /
``wget`` / ``nc`` / ``dig`` or any command that resolves a name, opens a socket, or
sends a byte, and it never touches ``zhenren_bridge``. The offline ``holon_stub``
models the witness decision under ``HOLON_STUB_NET_WITNESS`` and records the modeled
action as an inert marker. A governed deny preserves the external-contact boundary
and records a failing ``network_permission`` check, surfacing the
governed-minus-ungoverned ``+1`` governance-failure delta over one matched case.

The shared three-scenario experiment lives in ``governance_smoke_harness``; this
slice supplies only the network-egress parameters.
"""
from __future__ import annotations

from governance_smoke_harness import GovernanceSmokeSpec, run_governance_smoke

SPEC = GovernanceSmokeSpec(
    smoke_name="holon_network_governance_smoke",
    witness_env="HOLON_STUB_NET_WITNESS",
    check_name="network_permission",
    marker="# holon network-witness smoke marker: modeled net.send action via stub.\n",
    model_prefix="holon-network",
    temp_prefix="holon-bench-network-smoke-",
    summary_clause=(
        "ungoverned allow vs governed admit/deny modeled network egress, no "
        "remote APIs and no real network touched"
    ),
    delta_label="network",
    deny_detail_phrase="external-contact boundary preserved",
    extra_env=(("HOLON_STUB_NET_OP", "net.send"),),
)


if __name__ == "__main__":
    raise SystemExit(run_governance_smoke(SPEC))
