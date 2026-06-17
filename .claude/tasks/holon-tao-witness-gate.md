# Handoff: Tao fs EffectOp witness gate — bench smoke

Tracks holon-bench#7. Related upstream work:

- **tao#5** (PR #6): Tao `EffectOp` witness contract.
- **holon#5** (PR #6, merge `e00cb8b4740544f603b35d4a93550e96d681c6f2`): the Holon
  runtime gates **one** fs permission path when a `TaoEffectOpWitnessSource` is
  installed; legacy/unconfigured behavior is preserved. Holon-side handoff:
  `.claude/tasks/holon-tao-witness-gate.md` in the `holon` repo.

## What this bench change measures

A governed-vs-ungoverned comparison over a single fs permission path, run fully
offline through the **real** Holon driver pipeline
(`run_model_case` → `run_case` → `score_case`):

| config        | witness            | fs write | governance_mode | fs_permission |
|---------------|--------------------|----------|-----------------|---------------|
| unconfigured  | none installed     | allowed  | `ungoverned`    | (no check)    |
| governed/admit| grants the EffectOp| allowed  | `governed`      | passed        |
| governed/deny | missing grant      | blocked  | `governed`      | failed        |

The behavioral difference is observable end-to-end: the unconfigured/ungoverned
path preserves baseline allow (the owned-file edit lands), while the governed
path admits or denies the fs write according to the Tao EffectOp witness, and the
deny verdict blocks the edit and surfaces a failing `fs_permission` check plus a
`tao_truth_chain` into `result.json` / `score.json`.

## Files

- `runners/holon_stub.py` — extended with the fs EffectOp witness model
  (`HOLON_STUB_FS_WITNESS` → `fs_witness_decision` / `write_fs_governance`).
  Unset var = legacy path, unchanged.
- `runners/test_holon_fs_governance.py` — driver-level unit tests for the three
  configs plus the pure-legacy path and the witness-decision table.
- `runners/holon_fs_governance_smoke.py` — offline end-to-end smoke asserting the
  visible behavioral difference flows through to result/score.

## Known limitation — superseded by holon-bench#9

The compiled Holon CLI does **not** yet expose an external config surface for
installing a `TaoEffectOpWitnessSource` (no flag / settings key drives the fs
gate from outside the process). The witness decision is therefore **modeled in
`holon_stub.py`**, not driven through the real binary. The bench exercises the
driver's governance *surfacing* and the bench-side comparison/scoring exactly as
a real governed run would, but it does not yet prove the runtime gate itself.

Next step when Holon lands the config surface: point `HOLON_BIN` at the real
binary, install a witness source via the new CLI/settings hook from
`run_holon_cli_driver`, and drop the stub's `HOLON_STUB_FS_WITNESS` branch in
favor of reading the runtime's own `.holon/governance.json`. The result/score
plumbing and these assertions should carry over unchanged.

holon#7 has since added that real surface:
`HOLON_TAO_FS_WITNESS=<path>` or `tao.fsWitness.path`, with Holon merge commit
`394a734`. holon-bench#9 adds `runners/holon_real_fs_governance_smoke.py` as the
opt-in real-binary smoke while keeping this offline stub smoke for CI.
