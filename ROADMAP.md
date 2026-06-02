# Holon-Bench Roadmap

This roadmap keeps Holon-Bench focused on Holon's real operating target:
local models that can become reliable organs inside a self-improving agent
workflow. It is not a generic leaderboard plan.

## Evaluation Priorities

Holon-Bench should optimize for final task recovery through workflow, not
single-shot randomness. The key score distinction is:

- `first_pass`: the first submission passes all hard gates.
- `repaired_pass`: the submission passes after verifier-feedback repair.
- `repair_attempts_used`: the number of repair turns required.
- `final_fail`: the case still fails after exhausting the repair budget.
- `max_repair_exhausted`: the model failed within the configured repair limit.

Do not prioritize repeated stochastic trials for now. A model that can read
failures, repair its work, and converge is more useful to Holon than a model
with a slightly better one-shot sample rate.

## Test Hardening

Add hidden and mutation verifiers after the current public verifier path is
stable.

- Public verifier: visible to the agent for self-test and repair.
- Hidden verifier: final scoring gate for edge cases and regression coverage.
- Mutation verifier: robustness checks for scope traps, config variants,
  long-context noise, legacy debt, and safety constraints.

The goal is not leaderboard contamination resistance. The goal is to prevent
models from passing only the narrow visible test while violating the durable
workflow contract.

Verifier manifest contract:

```yaml
verifier:
  commands:
    - public verifier visible to the agent prompt
  hidden_commands:
    - final hidden gate, not shown in the agent prompt
  mutation_commands:
    - robustness gate for generated variants or trap checks
```

`hidden_commands` and `mutation_commands` are final scoring gates. They should
not be included in the prompt context. If they fail, the case must not count as
final-pass even when public verifier commands pass.

## Repair Cost Reporting

Every report should separate perfect convergence from cheap convergence.
`final_pass_rate` is not enough once verifier-feedback repair works.

Required repair-cost metrics:

- `first_failure_count`: cases that did not pass on the initial submission.
- `repaired_case_count`: first-fail cases recovered by repair.
- `total_repair_attempts`: total verifier-feedback turns spent.
- `repair_tax_rate`: repair attempts per benchmark case.
- `avg_repair_attempts_to_pass`: average attempts among repaired successes.

Interpretation:

- Low first-pass with high final-pass means the workflow is effective but
  operating cost is higher.
- High repair tax on one track means routing should reserve more wall-clock and
  token budget for that role.
- Repair success must still pass the same hard gates as first-pass success.

## Environment Isolation

Avoid making Docker mandatory. It is useful for reproducibility but too heavy
for the local iteration loop.

Use lightweight local isolation first:

- fresh temporary workspace per case
- fixture copy from clean source
- command timeout
- process-group cancellation
- resource guard
- command allowlist
- per-case environment manifest

Add an optional container backend later:

```yaml
environment:
  backend: local | container
  image: holon-bench/dev:latest
```

## DDD-First Workflow Track

Large system tasks should not jump straight into implementation. The workflow
must start from domain understanding and keep every later artifact traceable to
that domain model.

Canonical path:

```text
domain brief
-> DDD model
-> bounded contexts
-> ubiquitous language
-> spec.md
-> high_level_design.md
-> detailed_design.md
-> BDD scenarios
-> unit test plan
-> implementation
-> unit tests
-> BDD tests
-> final verification
```

Scoring dimensions:

- domain model correctness
- bounded-context clarity
- spec traceability
- design consistency
- implementation correctness
- unit test coverage
- BDD scenario coverage
- workflow artifact quality

This track is the basis for validating Holon's long-form self-iteration loop.

## Self-Bootstrap Track

Prefer self-bootstrap tasks over real-world issue porting. Real issue history
has realism, but it is less important than proving Holon can improve Holon.

Target case families:

- Holon modifies Holon workflow definitions.
- Holon extends Holon-Bench cases and verifiers.
- Holon diagnoses failed benchmark runs and patches runner logic.
- Holon creates a new tool contract and implements the tool.
- Holon updates routing recommendations from model score reports.

Required artifacts:

```text
diagnosis.md
plan.md
patch
regression test
verification.md
```

## Zhenren Upsampler Maintenance Track

`/home/taichi/zhenren-upsampler` should be evaluated as a maintenance and
architecture-refinement workload, not as a greenfield feature project.

Primary capability areas:

- log-driven root-cause diagnosis
- bug repair from user symptoms and runtime logs
- regression test creation
- config and CLI compatibility preservation
- pipeline refactoring without behavior drift
- backend abstraction cleanup
- quality-check and report integration
- performance and memory guard tuning
- resumability and partial-output recovery

Suggested scoring:

- root-cause accuracy: 25
- minimal patch correctness: 20
- regression protection: 15
- architecture improvement: 15
- log interpretation: 10
- config/CLI compatibility: 10
- observability: 5

Canonical case flow:

```text
symptom.md + log.txt + config excerpt
-> diagnosis.md
-> fix_plan.md
-> patch
-> regression_test
-> verification.md
```

## Martial RPG Simulation Track

The long-term game target is a Bevy plus authoritative game-server open-world
martial-arts RPG. The benchmark should test whether models can build combat
systems, simulation rules, and controller-driven martial input models.

Core domains:

- Bevy ECS gameplay architecture
- authoritative game server simulation
- deterministic tick, replay, and rollback
- controller input mapping
- animation state machines
- stamina, rooting, balance, centerline, and momentum
- hitbox, hurtbox, guard, parry, and throw resolution
- external styles, internal styles, taiji, sanshou, and push-hands modeling
- PvE sparring AI and behavior selection
- data-driven moveset authoring

Example case:

```text
Add a deterministic push-hands contact resolver.

Requirements:
- fighters maintain bridge contact points
- pressure vectors accumulate over ticks
- yielding reduces incoming force but changes root stability
- overcommitted forward pressure exposes balance
- replaying the same input stream produces the same outcome
- server and predicted client simulation agree on the result
```

Verifier shape:

```text
cargo test combat_push_hands
cargo test deterministic_replay
go test ./server/combat
```

This track should measure domain modeling quality as much as code generation.
