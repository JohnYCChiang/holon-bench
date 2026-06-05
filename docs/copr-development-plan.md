# COPR Development Plan for Holon-Bench

This plan turns the COPR discussion into a conservative implementation path for Holon-Bench.
The immediate goal is not to build the full Holon runtime. It is to make Holon-Bench accurately
measure agent workflow quality without mixing runner fallback behavior, hidden verifier leakage,
and uncontrolled model output.

## Guiding Principles

1. Separate two workflow meanings.
   - Single-LLM workflow: the internal cognitive order for one model call.
   - Holon-level workflow: the external engineered control loop around model calls, tools, artifacts, validators, and repair.

2. Keep prompt engineering as structured runtime input, not prose.
   - Kernel: stable behavior floor.
   - Workflow: per-call internal processing order.
   - Role: judgment lens.
   - Recipe: task technique fragment.
   - Tip: local, triggered reminder.
   - Output contract: hard stop and format brake.

3. Make Holon-level control explicit and testable.
   - No fallback path should silently change the benchmark mode.
   - No original fixture file should be accepted as a generated artifact.
   - No repair loop should depend on hidden verifier leakage.
   - Every behavior change needs a regression test.

4. Optimize local-model evaluation for clean attention and bounded output.
   - A cache hit is less important than avoiding context pollution.
   - Output budget control matters more than input prompt stability.
   - Each state should have a clear stop condition.

5. Put domain truth before executable specification.
   - Domain is the source of truth.
   - Specification is its executable shadow.
   - Code is its operational body.
   - Do not optimize the shadow or the body before validating the domain.

Chinese doctrine for Holon core prompts:

```text
領域為真，規格為影，程式為形。
先辨其真，再定其界，後成其形。
未明其真，不修其影；未定其界，不動其形。
```

This is not a request to force heavyweight tactical DDD patterns into every fixture.
It means every non-trivial workflow must first ask what domain it is changing, where that
domain boundary sits, which words have context-specific meaning, and which invariants must
not be broken. Small systems are not exempt; their domain model may simply collapse into a
single bounded context and remain lightweight.

## DDD-First Positioning

Holon-Bench should treat DDD as semantic governance and SDD as executable governance.

```text
DDD: define the world model.
  - core domain and subdomains
  - bounded contexts
  - ubiquitous language
  - aggregates, entities, value objects when useful
  - domain events, policies, and invariants

SDD: make that world model executable.
  - API and event schemas
  - state machines
  - contract tests
  - generated code
  - drift detection
  - AI implementation constraints
```

Implication for AI agents:

```text
Domain model
-> bounded context
-> context map
-> invariant
-> workflow / state machine
-> API / event / schema
-> test / contract / codegen
-> drift detection
```

Specs, tests, schemas, and APIs are projections of domain understanding. If the domain model is
wrong, stronger specification tooling only industrializes the wrong design. Holon-Bench should
therefore evaluate whether an agent preserves semantic boundaries, not only whether it satisfies
the nearest visible verifier.

## Current Problems To Resolve

The recent workflow experiment exposed three concrete runner issues.

1. `artifact` workflow timeout can fall through to `--print` and direct fallback.
   - Impact: one case can spend multiple full generation windows and mix evaluation modes.
   - Fix direction: once a controlled workflow is attempted, return its output or failure metadata; do not fallback to another generation path.

2. Existing solution files can be mistaken for generated workflow artifacts.
   - Impact: timeout or no-op generations can be scored against original fixture files.
   - Fix direction: artifact workflow should accept changed artifacts only. Existence-only recovery is allowed only where deliberately designed, such as graph recall workflow.

3. General artifact tasks have only a bounded implement state.
   - Impact: repair is still mostly orchestrated by `run_track.py`, so workflow trace and repair context are split across subprocesses.
   - Fix direction: add a controlled internal verify-review and repair flow without exposing hidden/mutation verifiers.

## Priority Roadmap

### P0: Stabilize Current Runner Semantics

Goal: make the current code honest before adding more features.

#### P0.1 Commit the runner bugfixes already identified

Scope:
- `runners/run_model_case.py`
- `runners/test_repair_pipeline.py`

Required behavior:
- Artifact workflow timeout does not invoke `holon --print`.
- Artifact workflow timeout does not invoke direct API fallback.
- Artifact workflow does not treat unchanged original fixture files as generated artifacts.
- Existing graph recall workflow recovery remains intact.

Validation:

```bash
python3 -m unittest discover -s runners -p 'test_*.py' -v
python3 runners/docs_check.py
```

Commit:

```text
Fix artifact workflow fallback recovery
```

#### P0.2 Clean report noise from code commits

Scope:
- Generated reports only.

Required behavior:
- Do not commit transient single-case experiment reports unless they are promoted to a named baseline.
- Keep aggregate reports only when intentionally updating published baseline summaries.

Validation:

```bash
git status --short
```

Commit:
- None by default. Reports are a separate baseline update.

#### P0.3 Add an explicit result metadata field for generation path

Scope:
- `runners/run_model_case.py`
- `schemas/result.schema.json` if needed
- tests

Add fields:

```json
{
  "generation_path": "direct | holon_auto | holon_workflow | holon_print | claw_cli",
  "fallback_used": false,
  "workflow_attempted": true,
  "workflow_type": "artifact | graph_recall | none"
}
```

Why:
- `driver=holon-cli` is not specific enough.
- Future comparisons must not infer path from trace files.

Validation:
- Unit test for direct, holon auto, artifact workflow, graph workflow, and fallback cases.
- One smoke case writes expected metadata.

Commit:

```text
Record generation path metadata
```

#### P0.4 Define HGP governance levels and telemetry fields

Scope:
- `docs/protocols/holon-governance-protocol.md`
- `docs/agent-governance-ladder.md`
- `runners/run_model_case.py`
- `runners/run_case.py`
- `runners/score_case.py`
- `runners/report.py`
- result and score schemas

Required behavior:
- Define HGP-L1 blackbox artifact, HGP-L2 graybox workspace, and HGP-L3 whitebox native.
- Record `governance_level` for every result and score.
- Preserve optional `prompt_stack` as nullable telemetry; do not fabricate prompt unit IDs for external drivers.
- Report governance-level and generation-path distributions in aggregate reports.

Why:
- External CLI agents such as Codex CLI, Claude Code, Antigravity CLI, and Aider should remain comparable through L1/L2 result and workspace governance.
- Holon-native runs can expose deeper L3 process telemetry without making it mandatory for black-box drivers.

Commit:

```text
Document HGP governance levels
```

### P1: Define Single-LLM COPR Units

Goal: make prompt behavior explicit without building a full prompt runtime yet.

#### P1.1 Add COPR and DDD doctrine spec document

Scope:
- `docs/copr-units.md`

Content:
- Kernel, Workflow, Role, Recipe, Tip, Output Contract definitions.
- Difference between single-LLM workflow and Holon-level workflow.
- DDD-first doctrine:
  - Domain before specification.
  - Boundary before implementation.
  - Language before code.
  - Invariant before workflow.
  - Specification is projection, not truth.
  - Small systems may be single-domain, not DDD-free.
- Token budgets for local models.
- Examples for implement, verify-review, and repair.

Validation:

```bash
python3 runners/docs_check.py
```

Commit:

```text
Document COPR and DDD prompt doctrine
```

#### P1.2 Add static prompt unit templates

Scope:
- new directory `prompt_units/`

Initial files:

```text
prompt_units/kernel/holon_bench_kernel_v1.yaml
prompt_units/kernel/domain_first_doctrine_v1.yaml
prompt_units/workflows/implement_artifact_v1.yaml
prompt_units/workflows/verify_review_v1.yaml
prompt_units/workflows/repair_artifact_v1.yaml
prompt_units/roles/patch_worker_v1.yaml
prompt_units/roles/reviewer_v1.yaml
prompt_units/roles/domain_modeler_v1.yaml
prompt_units/recipes/minimal_artifact_patch_v1.yaml
prompt_units/recipes/bounded_context_intake_v1.yaml
prompt_units/tips/output_no_markdown_fence_v1.yaml
prompt_units/tips/no_hidden_test_leakage_v1.yaml
prompt_units/tips/spec_is_projection_v1.yaml
```

Keep these small. This phase should not introduce dynamic selection yet.

Validation:
- YAML parse check.
- Schema-light check that every unit has `id`, `kind`, `version`, `content`, and `token_budget`.

Commit:

```text
Add initial COPR prompt units
```

#### P1.3 Wire static units into artifact workflow prompt assembly

Scope:
- `runners/run_model_case.py`
- tests

Required behavior:
- `write_artifact_workflow()` assembles implement instructions from fixed unit sections.
- Implement prompt includes internal workflow:

```text
Internally: domain -> boundary -> language -> invariants -> goal -> constraints -> evidence -> minimal design -> self-check -> artifact.
Output only complete owned file artifacts.
```

- It does not output the internal analysis.
- For small/simple cases, the model should keep DDD lightweight:

```text
If the domain is simple, identify the single bounded context in one internal step and proceed.
Do not introduce tactical DDD boilerplate unless needed by the task.
```

Validation:
- Unit test checks generated workflow JSON contains unit IDs in comments or metadata.
- Unit test checks output contract remains first-line artifact requirement.

Commit:

```text
Use COPR units for artifact implement prompt
```

### P1.4 Add a domain-intake single-LLM workflow fragment

Scope:
- prompt units
- `runners/run_model_case.py`
- tests

Purpose:
- Give implement/repair prompts a short internal domain-intake checklist without making every case a heavyweight DDD exercise.

Internal workflow:

```text
辨真: What domain behavior is affected?
定界: Which bounded context or ownership boundary applies?
正名: Which terms are context-specific?
守恆: Which invariants must not be broken?
成形: What is the smallest artifact that preserves the above?
校驗: Does the artifact satisfy the output contract and visible constraints?
```

Validation:
- Unit test generated implement prompt includes the compact doctrine.
- Unit test prompt still requires artifact-only output.

Commit:

```text
Add domain-intake workflow prompt fragment
```

### P2: Add Holon-Level Verify-Review and Repair Workflow

Goal: general artifact tasks should have a real workflow loop, not only external runner repair.

#### P2.1 Extend artifact workflow to implement -> verify_review

Scope:
- `runners/run_model_case.py`
- tests

Design:

```text
implement -> verify_review -> completed | failed_exit
```

`verify_review` behavior:
- Reviewer role.
- `permission_mode: danger-full-access`.
- Can run public verifier commands.
- Can inspect owned files.
- Can run small temporary edge checks derived from visible constraints.
- Must not edit source files.
- Must emit `VERIFY_VERDICT: PASS` or `VERIFY_VERDICT: FAIL`.

Important:
- Hidden and mutation verifier commands are still outside the model-visible workflow.

Validation:
- Generated workflow has `verify_review`.
- Public verifier commands are present.
- Hidden/mutation commands are absent.
- Trace contains verify state.

Commit:

```text
Add artifact verify-review workflow state
```

#### P2.2 Extend artifact workflow to implement -> verify_review -> repair

Scope:
- `runners/run_model_case.py`
- tests

Design:

```text
implement -> verify_review -> repair -> verify_review -> completed | failed_exit
```

`repair` behavior:
- Developer role.
- No source-edit tools unless artifact output is controlled by workflow.
- Reads previous owned artifact and verify output.
- Applies single-LLM repair workflow:

```text
failure -> violated requirement -> smallest correction -> self-check -> corrected artifact
```

Transitions:
- `verify_review` PASS -> `completed`
- `verify_review` FAIL -> `repair`
- repair retry limit 1 for now
- retry exhausted -> `failed_exit`

Validation:
- Unit test generated workflow transition graph.
- Unit test repair instructions include `output.verify_review`.
- Smoke case where public test fails first and repair gets feedback.

Commit:

```text
Add artifact repair workflow state
```

#### P2.3 Stop using external repair for workflow-native cases

Scope:
- `runners/run_track.py`
- `runners/run_model_case.py`
- scoring/report tests

Required behavior:
- If a case is run through workflow-native repair, `run_track.py` should not invoke a second `run_model_case.py` repair attempt for the same public verifier failure.
- External hidden/mutation failures may still be recorded as final gates.

Possible approach:
- Add result metadata:

```json
{
  "internal_repair_attempts_used": 1,
  "internal_verify_pass": true,
  "external_repair_attempts_used": 0
}
```

Validation:
- A workflow-native result does not spawn external repair.
- Non-workflow direct runs still use external repair when configured.

Commit:

```text
Separate internal and external repair accounting
```

### P3: Output Budget and Reasoning Budget Hygiene

Goal: stop relying on llama-server global settings where benchmark-level control is required.

#### P3.1 Record effective budget intent in metadata

Scope:
- `runners/run_model_case.py`

Add metadata:

```json
{
  "requested_thinking_budget": 768,
  "requested_max_output_tokens": 4096,
  "server_reasoning_budget_observed": null
}
```

Do not try to parse server logs in this phase.

Validation:
- Unit test metadata fields are present for workflow cases.

Commit:

```text
Record workflow budget metadata
```

#### P3.2 Add recommended server profiles

Scope:
- `docs/local-model-profiles.md`

Profiles:
- Qwen 35B MoE artifact workflow.
- Gemma 26B MoE artifact workflow.
- Small repair/reviewer profile.

Include warning:
- Some llama.cpp builds may not honor per-request `reasoning_budget`; server launch budget should match benchmark intent.

Validation:

```bash
python3 runners/docs_check.py
```

Commit:

```text
Document local model server profiles
```

### P4: Task Ledger MVP

Goal: move away from conversation history as state.

#### P4.1 Add per-case task ledger artifact

Scope:
- workflow JSON generation
- result metadata
- tests

Ledger fields:

```yaml
goal:
constraints:
owned_files:
domain:
  context:
  ubiquitous_language:
  invariants:
facts:
hypotheses:
failed_paths:
decisions:
public_verifier_results:
```

Start simple: generate `reports/task_ledger.json` in workflow workspace.

Validation:
- Workflow trace includes ledger artifact.
- Repair state receives ledger artifact.

Commit:

```text
Add task ledger artifact to workflows
```

#### P4.1a Add domain ledger fields before general ledger expansion

Scope:
- workflow generation
- result metadata
- tests

Fields:

```yaml
domain_context:
  name:
  confidence:
  reason:
ubiquitous_language:
  - term:
    meaning:
    context:
invariants:
  - claim:
    source:
    confidence:
boundary_notes:
  - claim:
    risk:
```

Rules:
- Facts and hypotheses must remain separate.
- Inferences about domain boundaries must not be recorded as facts without evidence.
- Small cases may record a single context and a short invariant list.

Validation:
- Unit test checks ledger schema.
- Prompt text asks the model to keep domain reasoning internal unless the workflow state asks for ledger output.

Commit:

```text
Add domain fields to workflow ledger
```

#### P4.2 Update verify-review to write task-state observations

Scope:
- workflow instructions
- artifact recovery

Required behavior:
- Reviewer output includes concise facts/hypotheses/failed paths.
- These are captured into ledger-like artifact or stdout metadata.

Validation:
- Unit tests for prompt text.
- Smoke test confirms ledger file exists.

Commit:

```text
Capture verify-review observations
```

### P5: Context Scheduling MVP

Goal: make context selection deterministic and phase-aware before building full scoring.

#### P5.1 Replace language-only context globs with decision profiles

Scope:
- `runners/run_model_case.py`

Profiles:

```text
implement_artifact:
  task contract / domain ledger / README / package manifest / owned src / visible tests

verify_review:
  domain ledger / owned src / visible tests / public verifier output / constraints

repair_artifact:
  domain ledger / owned src / previous artifact / verify output / constraints
```

Validation:
- Unit tests for selected context globs by state and language.

Commit:

```text
Add state-aware context profiles
```

#### P5.2 Add context budget caps

Scope:
- workflow generation
- docs

Add state-level budget intent:

```yaml
context_budget:
  max_input_chars: 40000
  evidence_priority:
    - owned_files
    - public_tests
    - README
```

If Holon workflow engine does not support this directly, record it in instructions and metadata first.

Validation:
- Unit tests check metadata and prompt text.

Commit:

```text
Add context budget hints to workflows
```

### P6: Prompt Unit Evaluation

Goal: make prompt engineering measurable.

#### P6.1 Add prompt unit IDs to reports

Scope:
- result metadata
- score/report aggregation

Report fields:

```json
{
  "prompt_units": [
    "holon_bench_kernel_v1",
    "implement_artifact_workflow_v1",
    "patch_worker_v1"
  ]
}
```

Validation:
- Unit tests.
- Report aggregation includes unit IDs without breaking old reports.

Commit:

```text
Record prompt unit usage
```

#### P6.2 Add unit effectiveness summary

Scope:
- `runners/report.py`

Output:
- pass/fail by prompt unit.
- average repair attempts by prompt unit.
- failure tags by prompt unit.

Validation:
- Synthetic score fixtures.

Commit:

```text
Report prompt unit effectiveness
```

### P7: Baseline Re-run Plan

Goal: produce trustworthy model comparisons after runner semantics are stable.

Run order:

1. Qwen 35B MoE, Q8 KV, artifact workflow, server reasoning budget 768.
2. Qwen 35B MoE, FP16 KV, same settings.
3. Gemma 26B MoE, FP16 KV, same settings.
4. Gemma 26B MoE, Q8 KV, same settings.
5. Gemma 12B dense, FP16/Q8 KV if useful.

Case order:

```text
py-tool-082
py-tool-048
bevy-002
go-game-028
then the previous 8-case sample
then full selected track subset
```

Rules:
- Same runner commit.
- Same workflow mode.
- Same generation timeout.
- Same repair budget.
- Same server reasoning budget unless the comparison is specifically about reasoning budget.
- Record model launch command in report notes.
- Record prompt unit IDs and domain doctrine version.

Commit:
- Only commit reports when promoted as a named baseline.

## Implementation Comfort Grain

Each implementation commit should satisfy:

- 1 behavior change.
- 1 focused regression test.
- No report churn unless the commit is explicitly a baseline report update.
- No model benchmark run required for pure runner refactors.
- At most one of these concerns per commit:
  - fallback semantics
  - artifact recovery
  - workflow graph generation
  - prompt unit content
  - scoring/reporting
  - docs

If a change cannot be explained in one sentence, split it.

## Done Criteria for COPR v0.1

COPR v0.1 is ready when:

1. Artifact cases run through a workflow with implement, verify-review, and repair states.
2. Single-LLM prompts include Kernel, Workflow, Role, Recipe, Tip, and Output Contract sections.
3. Hidden/mutation verifiers remain external and are never placed in model-visible context.
4. Runner metadata records generation path, workflow type, prompt unit IDs, and budget intent.
5. Timeout in one workflow state cannot trigger unrelated fallback paths.
6. Existing fixture files cannot be mistaken for generated artifacts.
7. Reports separate first-pass, internal repair, external hidden/mutation failure, and final pass.
8. At least one Qwen and one Gemma baseline are rerun under the same fixed workflow semantics.
9. Implement and repair prompts include the domain-first doctrine without forcing tactical DDD boilerplate.
10. Result metadata can distinguish domain facts, domain hypotheses, failed paths, and verifier results.

## Immediate Next Step

Do not start with model benchmarking.

First commit the current runner bugfixes with tests, then implement P0.3 generation path metadata. Only after the runner can tell exactly which path produced an artifact should workflow prompt improvements or model comparisons resume.
