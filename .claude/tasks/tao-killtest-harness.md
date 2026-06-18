# Request text: Tao kill-test harness (spike plan P4 / Appendix B)

**To use**: copy this file to `holon-bench/.claude/tasks/tao-killtest-harness.md`,
open a fresh session in `holon-world/holon-bench/`, and instruct:
「按照 .claude/tasks/tao-killtest-harness.md 執行」. Copying it there is the
explicit request the workspace rules require.

---

# Task: adapt Holon Bench to run the Tao Stage 0 kill test

Target layer: **holon-bench/ only**. Do not modify tao/ or holon/.

## Authority

`../tao/docs/tao-killtest-prereg-v0.md` is **FROZEN**: metrics M1–M11,
decision rule R1–R5 (with the 10% no-harm allowance), N=5 per arm, model
claude-fable-5, reviewer John. The harness implements it; it never
reinterprets it. Run-log minimal fields: `../tao/.claude/tasks/
tao-stage0-spike-plan.md` Appendix A.

## Two arms, identical task brief

- **Tao arm**: the agent acts ONLY through the `tao-port` CLI
  (`../tao/target/debug/tao-port`; build with `cargo build` in ../tao if
  missing). Per run: fresh `init --store <run-dir>/.tao`, trust the three
  tool_versions from `../tao/artifacts/trusted-toolchain-registry-v0.json`
  (SIGNED), then the agent loop: `txn` (JSON on stdin) · `check` · `test` ·
  `ctx` · `holes` · `discharge` · `node` · `facts`. Write an arm-specific
  **mechanics doc** describing these commands and the Txn/Node JSON shapes —
  its token cost counts into M1/M2 (prereg §5).
- **Baseline arm**: git text repo + repo map (Aider-grade) + Rust crate
  skeleton; agent edits files; `cargo test` runs the same suites (Rust
  rendition). Its mechanics doc is token-counted identically.

## Requirements

1. **Per-edit-cycle token accounting** (M1/M2): every token placed in the
   agent's context per edit cycle, including mechanics docs and diagnostics.
   Median + p90 computed per prereg §3.
2. **Run logging**: append-only JSONL per Appendix A fields; crashed and
   abandoned runs included; exact model ID recorded at first run.
3. **Suites**: arrive from the P2 session as `~/tao-killtest-private/` +
   `hashes.json`. Acceptance rendition is copied into arm-visible assets;
   the **hidden suite path is read only at scoring time from outside every
   arm mount and must never appear in any arm-visible file, prompt, or
   log** — leak ⇒ M10 void ⇒ INCONCLUSIVE. Record all suite hashes in the
   run log before run 1 (G3 witness).
4. **Tao-arm template instantiation**: acceptance/hidden Tao templates use
   placeholders `{EMPTY} {INSERT} {MEMBER} {SIZE} {EID} {prim:NAME}` —
   substitute from the run's world manifest + the agent's submitted def ids.
5. **Mutation runner** (M10): apply the P2 mutation specs per arm
   (AST-level node swap for Tao; source patch for Rust) to the final
   solution; a mutant is killed iff ≥1 test fails.
6. **Decoy dry-run mode** (P5): a different toy task for shakedown; decoy
   runs never touch the registered task or suites and never enter the
   experiment record.
7. **Scheduling + M5 packaging**: interleave arms; package final artifacts
   for arm-blind human review where the artifact allows; record review
   minutes.
8. Verifier round-trips (M4) = submit → structured-diagnostic/test-failure →
   resubmit cycles; count from the logs, not from agent self-report.

## Holon-Bench rules (unchanged)

Do not weaken validators or pass criteria; keep local-model support
agent-agnostic and OpenAI-compatible; add only backward-compatible result
metadata.

Validation: `python3 runners/schema_check.py .` · `python3 -m py_compile
runners/*.py` · `python3 runners/docs_check.py .` · `python3 runners/
ci_smoke.py .`

Deliverable: runnable harness + run-log writer. Stop before any real run:
P5 shakedown starts only after the prereg checklist surfaces (suite hashes
in run log, harness version hash recorded) are satisfied and the Legislator
confirms.
