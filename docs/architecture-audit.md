# Holon-Bench Architecture Audit

Status: current as of the Phase 2 / Tao-backed runtime baseline.

Holon-Bench evaluates agent behavior as a maintainer workflow, not as a single
completion. The core loop is:

```text
case definition -> generation driver -> verifier -> repair loop -> score/report
```

The design is organized around five commitments:

- complete patch or artifact workflows, not isolated answers
- hard gates plus soft metrics and role signals
- explicit scope control through allowed, forbidden, and protected paths
- public, hidden, and mutation verifier layers
- agent-agnostic execution through direct, CLI, and Holon-governed drivers

## Architecture

The repository has three main layers:

- **Definition layer**: manifests, schemas, cases, and fixtures describe what is
  measured and which artifacts are valid.
- **Execution layer**: runners generate artifacts, apply them in isolated
  workspaces, verify hard gates, and run bounded repair loops.
- **Reporting layer**: result and score records are aggregated into model
  matrices, routing recommendations, and governance comparisons.

The verifier stack is intentionally defense-in-depth:

```text
public verifier -> hidden verifier -> mutation verifier
```

Hidden verifiers are copied into the temporary workspace only for verification
and cleaned up afterward. This preserves repair feedback while reducing the
chance that an agent can train directly against private checks.

## Current Strengths

- **Agent-agnostic driver model**: raw OpenAI-compatible endpoints, CLI agents,
  and Holon-native workflows can be compared under one benchmark contract.
- **Repair-loop measurement**: `first_pass`, `repaired_pass`, and
  `repair_tax_rate` distinguish immediate correctness from recoverable but
  expensive behavior.
- **Scope safety**: scope gates catch forbidden, protected, and outside-allowed
  path edits before score aggregation.
- **Verifier depth**: hidden and mutation gates reveal public-test overfitting
  and semantic misses.
- **Structured failure taxonomy**: failure tags make benchmark output useful for
  routing and model improvement, not just pass/fail ranking.

## Canonical Metric Names

Use schema field names when documenting measurable benchmark outputs:

| Concept | Canonical field |
|---|---|
| First attempt trust | `first_pass` |
| Final verdict after repair | `final_pass` |
| Recovered by repair | `repaired_pass` |
| Repair-loop cost | `repair_tax_rate` |
| Scope safety | `scope_pass` |
| Hidden regression safety | `hidden_pass` |
| Mutation safety | `mutation_pass` |

Informal phrases such as "scope control" and "hidden verifier" are useful for
explaining intent, but they should not be written as metric names.

## Follow-Up Risks

- Keep `README.md`, protocol docs, and schemas aligned with the canonical metric
  names above.
- Treat generated files under `reports/` as run artifacts. Do not overwrite
  aggregate reports with a one-case exploratory run unless the commit is
  explicitly a report refresh.
- Strengthen schema validation only when the extra strictness is backed by
  manifest-derived checks or a stable enum source.
- Grow Phase 3 case coverage only after the existing hidden and mutation
  coverage remains visible in reports.
