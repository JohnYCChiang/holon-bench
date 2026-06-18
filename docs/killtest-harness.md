# Tao Stage 0 kill-test harness

Adapts Holon-Bench to run the **FROZEN** pre-registration in
`tao/docs/tao-killtest-prereg-v0.md` (spike plan P4 / Appendix B). The harness
*implements* the prereg; it never reinterprets it. Every threshold and metric
definition in `runners/killtest/config.py` is a transcription with a `prereg_ref`,
and the prereg file hash is stamped into the run log so any drift from the frozen
text is detectable (NT-15 discipline).

## Layout

```
runners/run_killtest.py        CLI entry point
runners/killtest/
  config.py     frozen constants, paths, provenance hashing
  tokens.py     per-edit-cycle token accounting (M1/M2)
  runlog.py     append-only JSONL writer (spike plan Appendix A)
  suites.py     suite hashing (G3), acceptance install, hidden isolation, leak scan
  templates.py  Tao template instantiation ({EMPTY}/{INSERT}/.../{prim:NAME})
  mutation.py   mutation runner (M10): Rust source-patch + Tao AST node swap
  scoring.py    per-run scoring: acceptance / hidden+mutation / defects
  arms.py       arm drivers + per-command instrumentation (ArmSession)
  schedule.py   interleave plan + arm-blind M5 review packaging
  checklist.py  pre-run gate (prereg §7 / spike plan P5)
  metrics.py    M1-M11 computation + R1-R5 decision rule
  decoy.py      decoy dry-run mode (never touches the registered task/suites)
  selftest.py   offline self-test of the pure logic
  assets/       arm-visible standing docs (task brief + per-arm mechanics)
```

## Two arms

* **Tao arm** acts only through `tao-port` (`tao/target/debug/tao-port`). A fresh
  `init --store <run>/.tao` per run; the harness trusts the three SIGNED
  `tool_version`s from the trusted-toolchain registry. The arm's mechanics doc is
  `assets/tao_mechanics.md`; its token cost is counted (prereg §5).
* **Baseline arm** is a git text repo + Aider-grade repo map + Rust crate; the
  agent edits files and `cargo test` runs the Rust rendition of the same suites.
  Mechanics doc: `assets/baseline_mechanics.md`, token-counted identically.

## Token accounting (M1/M2)

A single deterministic tokenizer (`holon-bench/regex-bpe-proxy-v1`) is applied to
the literal text *each* arm places in context — using one counter for both arms
is what makes R1/R2 comparable. Standing context (task brief + the arm's mechanics
doc) is counted into **every** edit cycle, because it really occupies the window
each cycle ("the Tao arm does not get its instruction manual for free", prereg
§5). `tao-port ctx` also reports its own bundle token count; that is logged as an
observational field (M7/M8), never as the M1/M2 number.

## Hidden-suite discipline

The acceptance rendition is the only suite copied into an arm mount. The
hidden/mutation suite is read **only at scoring time, only from outside every arm
mount**, and its path / case-ids never appear in any arm-visible file, prompt, or
log. `suites.scan_for_leak` enforces this; a leak voids M10 ⇒ INCONCLUSIVE.

## Operator flow

```
# G3 + provenance (before run 1)
python3 runners/run_killtest.py hashes
python3 runners/run_killtest.py init-experiment
python3 runners/run_killtest.py commit-suites --witness John

# per arm: install the arm-visible mount, then run the gate
python3 runners/run_killtest.py install-assets --arm tao --mount RUN/mounts/tao
python3 runners/run_killtest.py checklist --mounts RUN/mounts/tao RUN/mounts/baseline

# decoy shakedown (never enters the experiment record)
python3 runners/run_killtest.py decoy

# per run: session + instrumented commands + scoring
python3 runners/run_killtest.py start-run --run-id run-00-tao --arm tao --run-dir RUN/run-00-tao
python3 runners/run_killtest.py wrap --run-dir RUN/run-00-tao --arm tao --stdin txn < my.txn.json
python3 runners/run_killtest.py score --run-dir run-00-tao --arm tao

# verdict (mechanical; R1-R5)
python3 runners/run_killtest.py report
```

## Stop condition

This deliverable is the runnable harness + run-log writer. It does **not** execute
the real SortedUniqList experiment. P5 shakedown / P6 runs start only after
`checklist` reports `gate_pass: true` — which requires the suite-hash commitment
(G3), the harness version + model ID recorded, a clean leak scan, the SIGNED
toolchain registry (G5a), and a `LEGISLATOR_CONFIRMED.json` sentinel in the run
root. The decoy mode is the only thing safe to run before that gate.

## Decision rule (frozen, prereg §4)

`R1`: median(M1_T) ≤ 0.7·median(M1_B). `R2`: p90(M2_T) ≤ 0.8·p90(M2_B).
`R3/R5`: edits-to-green / review minutes not worse (≤110% baseline). `R4`: M10 not
worse and zero critical M11 defects. PASS = all five; `¬R1∨¬R2` = FAIL
(falsified); token-win but a no-harm loss = FAIL (cost relocation); missing data =
INCONCLUSIVE.
