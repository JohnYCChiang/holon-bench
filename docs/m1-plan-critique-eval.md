# M1 Plan-Critique: workflow integration + 4-model planning evaluation

Date: 2026-06-29. Models: 4 local Q8 tiers via llama.cpp (Vulkan), driven through
the holon-cli artifact workflow. Author: Claude (Opus 4.8).

## 1. What was built

`--plan-critique` flag (`runners/run_track.py` → `runners/run_model_case.py`, default
OFF, workflow byte-identical when off). When ON, the bench artifact workflow becomes a
two-state pipeline **`design_critique → implement`**:

- **`design_critique` state** runs holon's *official* plan-phase reviewer prompt (verbatim
  from `agent_definition/governance/runtime_prompts.yaml` `design_critique.system_prompt`):
  enumerate candidate designs, weigh memory-safety / `unsafe` / idiomaticity / complexity
  trade-offs, and **commit** to the safest viable design — output only the design, no code.
  It writes `reports/design_critique.md`.
- **`implement` state** gains `artifact_inputs: ["reports/design_critique.md"]`, threading
  the committed design into implementation (mirrors the existing graph-recall→implement
  two-state pattern).

The committed design is captured into the result meta's `artifact_snapshots` for offline
evaluation. **Zero holon changes** — this is the doctrine-compliant ("policy in
YAML/workflow units") way to give the workflow path a plan phase.

### Architecture note (corrects a misconception)
holon's M1 hook (`plan_critique`, `conversation/mod.rs:383-403`) lives in
`run_turn_internal`. The workflow engine's *generation* states reach it indirectly —
`engine.rs:215 prepare_teammate → teammate.rs:274 runtime.run_turn() → run_turn_internal` —
so M1 **does** fire in workflow runs when `HOLON_PLAN_CRITIQUE=1`. It simply never
*persists* the committed design (it is pushed into the system prompt and discarded). The
explicit `design_critique` state above is preferred because its output is a first-class,
captured workflow artifact.

## 2. Method

- Models (all Q8, reasoning off for plan generation, b/ub 2048/512):
  `qwythos` (9B dense, MTP), `gemma-12b` (12B dense), `gemma-review` (26B-A4B MoE, ~4B
  active), `qwen-deep` (35B-A3B MoE, ~3B active, MTP).
- Sample: stratified per-track ×3 = **39 cases** across all 13 tracks (easy/medium/hard).
- Designs captured: ~33/39 per model (config-only self_bootstrap cases produce no design);
  **32 cases have a committed design from all 4 models** — every one was read.
- Distinct `-plan` model names so results never collide with the no-plan G_off baseline.
  Caveat: `-plan` names fall to holon's default sampling policy (exact-match only), so all
  four share one sampling regime — internally consistent, but not each model's card values.

## 3. Verdict — planning quality

**Ranking: 26B-A4B > 35B > 12B ≫ 9B.** The user's hypothesis (the 26B "plans better")
holds — and strengthens on the full read: the 26B is the best *planner* for this benchmark.

| model | tier | planning | one-line characterization |
|---|---|---|---|
| gemma-review | 26B-A4B MoE | ★★★★½ | most disciplined/idiomatic/decisive; best plan→pass conversion |
| qwen-deep | 35B-A3B MoE | ★★★★ | deepest; best at subtle requirements + security decisiveness; over-engineers |
| gemma-12b | 12B dense | ★★★½ | competent, idiomatic, but enumerates without committing; shallower |
| qwythos | 9B dense | ★★ | fine on clear tasks; refuses / hallucinates / breaks persona on hard ones |

### Per-model, with evidence
- **26B-A4B** — consistently follows the M1 rubric, commits to the idiomatic-minimal
  solution, rarely over-reaches. Passes where others fail by being decisive without scope
  creep: `bevy-008` (system splitting), `go-core-009` (type-assertion interface upgrade —
  "the Go way"), `py-tool-033` (`Result` + `is_relative_to`). The "senior maintainer"
  archetype the prompt asks for.
- **35B** — the deepest analysis and best requirement-capture: only model to reach for
  `Decimal` + daily-limit **date reset** (`ddd-first-002`), a bounded 8KB binary sniff
  (`py-tool-009`), removing the `ClientDamage` field outright for the authoritative-damage
  fix (`martial-rpg-002`). But its thoroughness backfires: custom `RetryFuture` impl
  (`rs-port-024`), extra global registries/indexes (`go-game-003/009`) added scope and the
  implementations failed.
- **12B** — solid and idiomatic but frequently stays in "here are 3-4 options" mode without
  the crisp COMMIT the prompt demands (`py-tool-033`, `py-tool-009`, `flutter-018`).
- **9B** — adequate on easy, well-specified tasks (ddd-first-008, flutter-011, oss-maint-004,
  self-boot-006/001 all pass) but collapses on hard/underspecified ones: **refuses / asks for
  context that is already present** (oss-maint-002, bevy-015, rs-core-007, rs-port-001),
  **hallucinates APIs** (`tokio::time::Retry` in rs-port-024 — does not exist), **breaks
  persona** ("I am Qwythos, an AI model created by Empero AI…" in bevy-002), and rambles
  without committing (go-core-009).

### Differentiating dimensions (what actually separates them)
1. **Decisiveness / commitment.** 35B & 26B commit crisply; 12B enumerates; 9B sometimes
   never commits. The prompt explicitly asks to COMMIT — 26B/35B honour it best.
2. **Underspecified-task handling** — the sharpest divider. When a task implies context the
   model must infer, 9B refuses or speculates; the other three proceed on reasonable
   assumptions. This is 9B's most damaging weakness.
3. **Over-engineering vs minimalism.** 35B richest (sometimes too rich → failed exec); 26B
   hits the idiomatic-minimal sweet spot best.
4. **Safety stance is NON-differentiating** — every model (even 9B) avoids `unsafe`. The M1
   prompt's safety/idiomaticity steer lands on all of them; the real signal is requirement
   capture, decisiveness, and not hallucinating.

## 3a. Plan-best ≠ code-best (planner/executor split)

Raw implementation skill (G_off, no plan — the model writes code directly) inverts the
planning ranking, on the **same 130 cases**:

| model | plan quality (design text) | code quality (G_off pass) |
|---|---|---|
| 35B (qwen-deep) | ★★★★ (over-engineers) | **65%** ← best implementer |
| 12B (gemma-12b) | ★★★½ | 61% |
| 26B-A4B (gemma-review) | ★★★★½ ← best planner | 58% ← weakest of the strong |

**Best planner ≠ best coder.** Suggestive (not clean) corroboration: the design-critique
moved 26B-A4B 58%→64% but 35B 65%→54% (its over-engineered plan appears to mislead its
strong implementation) — confounded by the 39-case subset + default sampling, so only the
"35B best raw coder" half is firm.

**Implication — planner/executor split:** 26B-A4B plans → 35B implements, matching holon's
model-policy roles (qwen=architect, gemma=executor). Owed experiment: feed 26B's committed
design into 35B's implement state and check it beats either alone. Hardware blocker first
(see below): both Q8 models (~26 GB + ~37 GB) exceed this APU's 62 GB GPU-addressable UMA.

## 4. Takeaways for the M1 default-on question
- Plan quality tracks outcome quality (26B/35B/12B plan well and pass more; 9B plans poorly
  and passes least), supporting M1's premise that a committed design helps.
- M1's steer reliably pushes **every** model toward safe, idiomatic designs — its clearest,
  most uniform effect.
- A rigorous pass-rate delta (with-plan vs no-plan, same cases, same sampling) is still
  owed: the current `-plan` arm uses a 39-case subset + default sampling, so it is not a
  clean A/B against the 130-case G_off baseline. Recommended next step before any default-on
  decision: a matched same-case, same-sampling with/without-plan run.

## 5. Artifacts
- Feature: commit `bench: optional M1 design-critique state in the artifact workflow`.
- Captured designs: `reports/<model>-plan_holon-cli_artifact_<case>_artifact.txt.meta.json`
  (`artifact_snapshots` → `reports/design_critique.md`).
- No-plan baseline (G_off): `reports/<model>_holon-cli_artifact_*` for gemma-12b /
  gemma-review / qwen-deep (130 each) + qwythos (partial).
