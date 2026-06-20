#!/usr/bin/env python3
"""Offline governed-vs-ungoverned smoke for the Holon fs *write* permission path.

Holon#5 (merge e00cb8b) gates one fs permission path through a Tao
``TaoEffectOpWitnessSource`` when one is installed, while preserving the legacy
behavior when it is not (tao#5 defines the ``EffectOp`` witness contract). The
compiled Holon CLI does not yet expose an external config surface for installing a
witness source, so this smoke models the witness decision in the offline
``holon_stub`` and drives all three configurations (unconfigured / governed-admit /
governed-deny) through the *real* Holon driver -> verifier -> result -> score
pipeline, with no remote API, model endpoint, or compiled Holon binary. The
governed runs surface exactly the one fs-write denial the ungoverned baseline
silently allowed (governance-failure delta ``+1`` over one matched case).

The shared three-scenario experiment lives in ``governance_smoke_harness``; this
slice supplies only the fs-write parameters. The generic governance surfacing smoke
is ``holon_smoke.py``; this one isolates the fs-write EffectOp gate specifically.
"""
from __future__ import annotations

from governance_smoke_harness import GovernanceSmokeSpec, run_governance_smoke

SPEC = GovernanceSmokeSpec(
    smoke_name="holon_fs_governance_smoke",
    witness_env="HOLON_STUB_FS_WITNESS",
    check_name="fs_permission",
    marker="# holon fs-witness smoke marker: gated owned-file change via stub.\n",
    model_prefix="holon-fs",
    temp_prefix="holon-bench-fs-smoke-",
    summary_clause="ungoverned allow vs governed admit/deny, no remote APIs",
    delta_label="fs",
)


if __name__ == "__main__":
    raise SystemExit(run_governance_smoke(SPEC))
