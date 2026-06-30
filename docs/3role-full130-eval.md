# 3-Role Pipeline (PM→HLD→Implement) vs Single Model — full-130 evaluation

Date: 2026-06-30. Author: Claude (Opus 4.8). Driver: holon-cli artifact workflow,
local Q8 models via llama.cpp (Vulkan). Models: `qwen-deep` (Qwen3.6-35B-A3B-MTP) at
8081, `gemma-review` (gemma-4-26B-A4B) at 8082, co-resident (100 GB GTT).

## What was tested

A 3-role **holon workflow** (`--pm-hld-pipeline`, pure WorkflowState composition, zero
holon changes): `pm` (35B, requirements + acceptance, WHAT only) → `hld` (26B, high-level
design, the architect) → `implement` (35B, detail design + code). Each role is routed to
its evidenced strength (see `docs/m1-plan-critique-eval.md`): 35B is the best
requirement-capturer *and* best implementer; 26B is the most decisive designer. The
engineer owns DETAIL design (so the 26B HLD stays high-level — no off-idiom mismatch).

Two thinking configs, controlled at server level (the only reliable on/off lever on this
Qwen build — `thinking_budget=0` and `/no_think` were both verified ineffective):

- **C1 all-on**: 35B + 26B both `--reasoning auto` (pm, hld, implement all think).
- **C2 architect-only**: 35B `--reasoning off`, 26B `--reasoning auto` (only HLD thinks;
  pm + implement are non-thinking). PM and implement share the 35B server, so they cannot
  differ in thinking — C2 is "both 35B stages off", not "PM-only off".

Baseline: single-model 35B writing code directly (G_off, one implement state) = the
existing 130-case run.

## Headline result (full 130 cases)

| config | pass | vs single |
|---|---|---|
| **single-model 35B** (1 implement state) | **85/130 = 65%** | — |
| C1 all-on (3-role) | 74/130 = 57% | **−8 pts** |
| C2 architect-only (3-role) | 72/130 = 55% | −10 pts |

**On a realistic mixed workload, the 3-role pipeline LOSES to the single strong model.**
Thinking config barely matters: C1 (57%) vs C2 (55%) is **net −2 (gained 9, lost 11) —
inside the noise band** (see below). The expensive all-thinking config buys nothing over
the cheaper architect-only one.

## Two findings that explain it

### 1. ~15% run-to-run variance (the pipeline is highly stochastic)
The same all-on config, run twice, on the same 65 "discriminating" cases:
**38% (primary run) vs 29% (full-130 run) — 10/65 cases flipped (15%).** The workflow runs
at the holon persona default **temperature 0.7** (`persona.rs` `_ => 0.7` for the
Developer/Reviewer roles — NOT the `--temperature 0.1` CLI flag, which only reaches the
direct driver, not the holon_workflow path; WorkflowState has no temperature field). At
0.7 — near this MTP model's natural operating point (~0.6) — sampling variance is
**inherent**, and the 3-role pipeline AMPLIFIES it: a one-token divergence in the PM brief
cascades through HLD and implement into a wholly different solution, where the single model
(one generation) diverges far less. Single-run margins of ±5–10 cases are therefore
**mostly noise**. An earlier "3-role beats single by +7 on the hard subset" claim was a
lucky run; it does not survive a second run. Both arms use the same path/temperature, so
the single-vs-3-role comparison is fair — but both are single noisy samples.

### 2. The pipeline TRADES cases — rescues hard ones, breaks easy ones
Splitting the 130 into the 65 "discriminating" (hard) and 65 "easy" (single solves all):

| | easy 65 | hard 65 |
|---|---|---|
| single | **65/65** | 20/65 |
| C1 all-on | **55/65** ← breaks 10 | 19/65 |

The overhead and stochasticity of three stages **introduce failures on simple,
well-specified tasks that the single model nails reliably** (easy-case variance ≈ 0 for
single). On hard cases the pipeline is within noise of single. Net: across all 130 the
3-role **rescues 9** cases single fails (martial-rpg, some flutter/go-core/rs-core) but
**breaks 11** easy/medium cases — a net loss on a mixed population.

### Per-track (single / C1 / C2)
```
martial_rpg              8 / 9 / 10   <- the one track 3-role consistently HELPS
oss_maintenance         10 /10 /10
graph_memory_workflow   10 / 9 / 9
ddd_first                7 / 6 / 6
go_game_server           6 / 5 / 5
rust_bevy                9 / 8 / 8
self_bootstrap           5 / 4 / 4
flutter_cross_platform   7 / 5 / 5    <- regression
rust_core                9 / 8 / 7    <- regression
go_core                  8 / 6 / 4    <- regression
python_tool_engineering  6 / 4 / 4    <- regression
repair_needed            0 / 0 / 0    <- hard floor (no config solves)
rust_porting             0 / 0 / 0    <- hard floor
```

## The real opportunity is ensemble, not a cleverer pipeline

The variance and the rescue/break trade-off both point the same way: a single fixed
pipeline will not beat a strong model on a mixed workload, but **diversity + selection**
will. Treating single + C1 + C2 as three samples:

| metric | pass |
|---|---|
| single (1 run) | 85 (65%) |
| **ANY-of-3 passes (oracle ceiling)** | **94 (72%)** |
| ≥2-of-3 (robust / majority) | 78 (60%) |
| all-3 pass (rock-solid) | 59 (45%) |

The oracle ceiling is +7 over single. Because there is **no QA loop** (single-shot, the
model never sees a test), **agreement across runs is the available no-test quality
signal** — ≥2/3 and all-3 stratify confidence. Best-of-N / self-consistency voting (or a
selection state over diverse generators) is where the gains are.

## Recommendation
- **Default to the single strong model** on mixed/unknown workloads; the 3-role pipeline
  is net-negative across the board and costs ~3× wall-clock (three serial stages).
- Use the 3-role pipeline **selectively** on identified hard / design-heavy cases (it
  rescues martial-rpg and some design-y tracks), ideally inside an **ensemble with
  selection**, not as the unconditional path.
- **Do not over-read single-run deltas** under ~15%: they are noise. Lowering to greedy is
  the wrong fix for this MTP model (its draft is tuned for ~0.6; greedy distorts it). The
  right fix is **N repeated runs at temp 0.6 + majority vote**, which both denoises and is
  the ensemble lever. Setting 0.6 requires a holon change — the bench cannot override the
  persona temperature (WorkflowState has no temperature field; it is `_ => 0.7` in
  `persona.rs`).

## Artifacts
- Feature (uncommitted, validated, backward-compatible): `--pm-hld-pipeline` +
  per-role `--pm/hld/executor-thinking-budget`, `--hld-model/--hld-endpoint` in
  `runners/run_model_case.py` + `runners/run_track.py`.
- Results: `reports/full130_allon/`, `reports/full130_archonly/`,
  `reports/goff_qwen_backup/` (single). Report tool: `full130_report.py`.
- Caveat: 1 C2 case (`ddd-first-010`) remained banner-truncated after auto-rerun; C2 is
  effectively 72–73/130. Does not change conclusions.
