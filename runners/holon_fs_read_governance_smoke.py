#!/usr/bin/env python3
"""Offline governed-vs-ungoverned smoke for the Holon fs *read* permission path.

The read-side sibling of ``holon_fs_governance_smoke.py``. Where that smoke gates
an fs *write* (mutation), this one gates an fs *read* -- the information boundary /
context-exposure case. tao#18 defines the fs-read tiers ``fs.stat | fs.list |
fs.read``; holon#11 maps ``read_file`` / ``grep_search`` to ``fs.read`` and
``glob_search`` to ``fs.list``, reusing the same ``tao.fsWitness`` config/witness
shape as the write gate.

The witness *decision* logic is identical to the write slice; only the framing
differs. A read deny does not block a mutation -- it blocks the *context exposure*:
the file's contents are never surfaced into the agent's run artifact. The offline
``holon_stub`` models this with ``HOLON_STUB_FS_KIND=read``, which records an
``fs_read_permission`` check while reusing the same allow/deny path. The governed
runs surface exactly the one read denial the ungoverned baseline silently allowed
(governance-failure delta ``+1`` over one matched case).

The shared three-scenario experiment lives in ``governance_smoke_harness``; this
slice supplies only the fs-read parameters.
"""
from __future__ import annotations

from governance_smoke_harness import GovernanceSmokeSpec, run_governance_smoke

SPEC = GovernanceSmokeSpec(
    smoke_name="holon_fs_read_governance_smoke",
    witness_env="HOLON_STUB_FS_WITNESS",
    check_name="fs_read_permission",
    marker="# holon fs-read smoke marker: exposed file contents via gated read.\n",
    model_prefix="holon-fs-read",
    temp_prefix="holon-bench-fs-read-smoke-",
    summary_clause=(
        "ungoverned allow vs governed admit/deny context exposure, no remote APIs"
    ),
    delta_label="fs-read",
    deny_detail_phrase="context exposure blocked",
    # Read slice: frame the witness gate as an fs.read context exposure.
    extra_env=(("HOLON_STUB_FS_KIND", "read"),),
)


if __name__ == "__main__":
    raise SystemExit(run_governance_smoke(SPEC))
