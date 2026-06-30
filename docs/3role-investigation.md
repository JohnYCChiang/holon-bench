# 3-Role Pipeline Investigation: what "regression" really was, and the spec-precision problem

Date: 2026-06-30. Author: Claude (Opus 4.8), driven by the maintainer's challenges.
Models: local Q8 via llama.cpp — `qwen-deep` (Qwen3.6-35B-A3B-MTP) + `gemma-review`
(gemma-4-26B-A4B), holon-cli artifact workflow. Companion: `docs/3role-full130-eval.md`.

## TL;DR

A PM→HLD→implement holon workflow *appeared* to lose to the single strong model on the
full 130 (57% vs 65%). Pulling that thread apart, **every identifiable cause of the
apparent regression was a measurement or setup defect on our side, not an inherent cost of
decomposition** — and the deepest residual is a **benchmark-fairness problem**: for a class
of cases the precise contract lives only in the hidden/mutation test, not in the spec the
model is given. No pipeline can derive what the spec omits.

## 1. The headline reversal: single-run comparisons are noise

The pipeline runs at the holon persona temperature **0.7** (not the CLI `--temperature 0.1`,
which never reaches the workflow path — `persona.rs` `_ => 0.7`; now set to **0.6**, the
MTP model's point). At that temperature, three compounding stochastic generations give
**~15% run-to-run variance**: the same all-on config scored 38% then 29% on the same 65
hard cases.

The killer: re-running the **single** baseline 3× on the cases it "won" showed it is *not*
reliable there — go-core-004 **0/3**, go-game-028 **1/3**, py-tool-010 **1/3** — yet the
recorded baseline marked all three PASS. **The baseline captured single's lucky samples;
comparing them to one pipeline run manufactured an illusion of regression.** Any verdict
needs multi-run pass-rates on both sides.

## 2. Anatomy of the 11 "regressions" — all confounds

Of 11 cases where single's baseline passed but the 3-role failed:

| cause | cases | nature |
|---|---|---|
| **DOMAIN.md starved** | ddd-first-017 (+ all ddd) | benchmark setup bug (mine) |
| **execution crash** | go-core-004, py-tool-010 (intermittent) | pipeline setup bug (mine) |
| **over-engineering** | go-core-004, go-game-028 | prompt (mine) |
| **idiomatic rewrite** | py-tool-010 | prompt (mine) |
| **contract softening** | ddd-first-017 | prompt (mine) |
| **run-to-run variance** | flutter-054, go-core-009, go-core-110 | noise |

Each is described below; each was removed by a fix, and the apparent deficit shrank each
time.

- **DOMAIN.md starvation.** All 40 ddd cases say "Follow DOMAIN.md", mark DOMAIN.md
  `forbidden` (do-not-edit, not hidden), yet `benchmark_context_globs_for_case` globbed only
  `README.md` (which these fixtures don't even have). The model was told to follow a file it
  could not read; it recovered the spec by Python convention. Fix: added `DOMAIN.md` to the
  context globs. ddd-first-017 then went FAIL→PASS (the engineer read "ValueError otherwise"
  and raised).
- **Execution crash = "truncation".** The banner-only artifact (`🚀 [Workflow] Initiating…`)
  is not a timeout — it is the HLD state's model emitting a tool-use block in a
  `allowed_tools:[]`, `max_iterations:1` state; holon treats a pending tool-use as "continue"
  and trips "conversation loop exceeded the maximum number of iterations". Root cause: PM/HLD
  had **no `context_globs`** yet were told to "reuse existing code" → they tool-seek. Fix:
  gave PM/HLD the code context + `max_iterations:3`. Crash gone.
- **Over-engineering / idiomatic-rewrite / contract-softening** were all prompt defects: the
  HLD "design structure" framing invented error hierarchies and registries; "prefer
  idiomatic" licensed behavior-changing rewrites (py-tool-010 `{**DEFAULTS}` reorders keys);
  "no edge cases / define WHAT" softened "raises ValueError" to "rejects". Fixed by the
  maintainer-minimal principle ("smallest change; reuse existing unchanged; restyle nothing;
  carry the exact contract").

Testing whether the HLD stage was a net leak (`--no-hld`, PM→implement direct) did **not**
help and made go-game-028 worse — so the residual misses are not specifically the HLD.

## 3. The redesign (the maintainer's): contract crystallized, not paraphrased

Prose handoffs (REQUIREMENTS / HLD) lose precision at each step. The fix is to make each
role's artifact progressively more concrete and executable:

- **PM → BDD.** Turn the task into `Given/When/Then` scenarios (incl. exact error + state
  after failure). Drift can't survive a scenario: `Given a negative reading … Then raises
  ValueError, And state unchanged`.
- **Architect → Domain model (DDD).** From the BDD, state entities, value objects, and
  precise invariants — this *reconstructs* DOMAIN.md from the scenarios.
- **Engineer → TDD.** First turn every scenario + invariant into concrete assertions, then
  implement the smallest change that makes all hold, then **adversarially self-review** (find
  the input most likely to break each, trace it, fix). Verified mechanically: go-game-028's
  BDD chain produced the remove-**all** filter (matching single's passing version), not the
  remove-first drift.
- **(B) verifier-driven repair** — holon-bench's core — feeds back **public-verifier** output
  only (hidden/mutation are oracles; leaking them would teach to the test). It fixes
  public-test failures (py-tool-010 FAIL→PASS via repair) but is, by design, powerless on
  cases that pass public and fail mutation.

## 4. The deepest finding: precise contracts hidden in tests (fairness audit)

The mutation-only failures led to a static audit (spec vs hidden/mutation test) of the 14
cases where single passed the public verifier but failed a hidden gate. Verdicts:

**UNDER-SPECIFIED — the hidden test enforces a behavior absent from the spec (4):**
- **go-core-004** — mutation requires path-context wrapping on *validation* branches that
  swallow no underlying error; task only says "preserve … the underlying error"; visible
  test accepts the bare sentinel.
- **bevy-002** — negative `apply_damage` must not heal; only in the mutation test.
- **go-game-110** — exact pinned LCG outputs `175,78,841`; no constants given anywhere —
  unguessable.
- **go-game-009** — reconnect must *extend the TTL*; never stated.

**BORDERLINE — idiomatic or implied, but stated only in the hidden test (5):**
py-tool-101 / py-tool-102 (exact error-code magic strings, e.g. `invalid_returncode`,
`unsafe_arg`), go-game-052 (`Removed` sorted alphabetically), go-game-014 (closed channel
stops the loop), flutter-018 (failure clears the in-flight coalescing slot).

**FAIR — every hidden assertion traces to an explicit constraint / DOMAIN.md (6):**
ddd-first-006, ddd-first-010, flutter-122, py-tool-122, self-boot-002, self-boot-003.
(Note: the two ddd cases are fair *because* DOMAIN.md enumerates the contract — and DOMAIN.md
was the file we were withholding until §2's fix.)

**9 of 14 carry some under-specification, all of one shape: the precise contract lives in the
hidden test, while the model is given ambiguous prose.** Recurring classes: (1) exact
error-code/magic strings, (2) unguessable pinned values, (3) behavior on a branch/input the
spec never mentions, (4) determinism/ordering details.

### The clean separator
The full stack (BDD + Domain + TDD + self-review + repair) lifts the **fair** cases
(go-game-028, py-tool-010 pass) but **cannot** lift go-core-004 (0/2) — because no pipeline
can derive a contract the spec omits. This empirically separates *model/pipeline limitation*
(fixable by a better pipeline) from *benchmark under-specification* (fixable only by fixing
the spec).

## 5. Recommendations

1. **Express the contract in the spec, BDD-style.** The precise behavior the hidden tests
   check (error codes, ordering, branch behavior, boundaries) should appear as Given/When/Then
   in the case `user_request`/`constraints` — not be discoverable only by reading the hidden
   test. This both makes the benchmark fair and removes the interpretation noise.
2. **Fix the 4 under-specified + 5 borderline cases** (above) — either state the contract or
   loosen the hidden assertion to what the spec determines. `go-game-110`'s pinned LCG
   constants in particular are unguessable and should be given or dropped.
3. **Never compare single-run pass/fail.** Use N-run pass-rates on both arms; the per-case
   variance at temp 0.6–0.7 is ~15%, larger than most measured deltas.
4. **The BDD/Domain/TDD/self-review/repair pipeline is sound** and is the right shape for
   maintainer-style work; evaluate it (vs single) only under #3, after #1–#2.

## Artifacts
- Code (uncommitted, validated): `--pm-hld-pipeline` 3-role workflow with per-role BDD/Domain/
  TDD prompts, `--no-hld`, per-role `--pm/hld/executor-thinking-budget`, `context_globs` +
  `max_iterations:3` on PM/HLD; `DOMAIN.md` added to `benchmark_context_globs_for_case`;
  holon `persona.rs` `_ => 0.6`.
- Result dirs under `reports/`: `full130_allon`, `full130_archonly`, `v8_bdd`, `v9_repair`,
  `v10_introspect`, `single_rep`, `v2_regression_uglyprompt`, `v3_clean_failed`.
