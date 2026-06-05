# Holon Governance Protocol v0.1

Holon Governance Protocol (HGP) defines how an AI coding agent can be evaluated,
repaired, audited, and compared under maintainer-style constraints.

HGP is not a tool protocol and not a model API. It is a governance protocol for
verifiable agent outputs, workspace behavior, repair loops, and native process telemetry.

```text
MCP lets agents access capabilities.
HGP proves what agents actually did.
```

## Goals

- Make agent outputs verifiable.
- Separate result governance from process governance.
- Support black-box, gray-box, and white-box agents.
- Standardize repair feedback and repair cost accounting.
- Preserve compatibility with external CLI agents.
- Avoid requiring private chain-of-thought.

## Non-Goals

- HGP does not define an LLM chat API.
- HGP does not replace MCP or other tool protocols.
- HGP does not require agents to expose hidden reasoning.
- HGP does not require every driver to expose Holon-native telemetry.
- HGP does not trust an agent's self-reported success without verifier evidence.

## Levels

HGP has three levels.

| Level | Name | Purpose |
| --- | --- | --- |
| HGP-L1 | Artifact Protocol | Verify final patch or artifact output. |
| HGP-L2 | Workspace Protocol | Audit external CLI behavior in a temporary workspace. |
| HGP-L3 | Native Telemetry Protocol | Audit Holon-native process telemetry and COPR usage. |

## HGP-L1: Artifact Protocol

HGP-L1 is the most portable layer. Any agent can participate if it emits a patch or
artifact submission.

```yaml
protocol: hgp-l1-artifact
version: 0.1
input:
  case_id: string
  task_prompt: string
  workspace_snapshot: path
  allowed_paths: list[string]
  forbidden_paths: list[string]
output:
  kind: patch | artifact
  file: path
  optional_meta: path
required_properties:
  - output_applies_or_parses
  - no_required_internal_trace
```

Holon-Bench owns:

- patch or artifact application
- schema checks
- scope checks
- visible verifier commands
- hidden verifier commands
- mutation verifier commands
- semantic checks
- failure taxonomy
- repair feedback generation

HGP-L1 can prove result correctness. It cannot prove process quality.

## HGP-L2: Workspace Protocol

HGP-L2 is for external CLI agents. The agent runs in a temporary workspace and
Holon-Bench audits the workspace before and after execution.

```yaml
protocol: hgp-l2-workspace
version: 0.1
input:
  workspace_root: path
  task_prompt: string
  timeout_seconds: int
  allowed_paths: list[string]
  forbidden_paths: list[string]
  repair_feedback: optional[string]
execution:
  non_interactive: true
  cwd: workspace_root
  network_policy: declared
  write_policy: workspace_only
output:
  changed_files: git status
  diff: git diff
  stdout: captured
  stderr: captured
  artifacts: optional[list[path]]
  exit_code: int
```

HGP-L2 can prove result correctness and workspace behavior. It cannot reliably prove
internal prompt stack, context selection, private tool trace, or model routing.

## HGP-L3: Native Telemetry Protocol

HGP-L3 is for Holon-native workflow runs or any agent that exports compatible telemetry.

```yaml
protocol: hgp-l3-native
version: 0.1
input:
  task_contract:
    goal: string
    allowed_paths: list[string]
    forbidden_paths: list[string]
    protected_paths: list[string]
    verifier_visible: list[command]
    verifier_hidden_declared: bool
output:
  artifact:
    kind: patch | artifact
    path: string
  telemetry:
    prompt_stack:
      kernel: string
      workflow: string
      role: string
      recipe: list[string]
      tips: list[string]
      output_contract: string
    model_route:
      model: string
      provider: string
      reason: string
    context_pack:
      sections:
        - id: string
          kind: string
          token_estimate: int
          source: string
    tool_trace:
      - tool: string
        input_summary: string
        output_summary: string
        success: bool
    validation_trace:
      - validator: string
        pass: bool
        failure_tags: list[string]
    repair_trace:
      attempts: int
      feedback_used: list[string]
    ledger_delta:
      facts_added: list[string]
      hypotheses_added: list[string]
      failed_paths_added: list[string]
```

HGP-L3 can prove result correctness, workspace behavior, and process provenance.

## Common Concepts

### Case

A case is a fixture plus a task contract, scope policy, verifier commands, semantic
checks, and scoring rubric.

### Attempt

An attempt is one generation pass. The first attempt determines `first_pass`. Later
attempts are repair attempts.

### Artifact

An artifact is either:

- a unified diff patch
- a complete owned-file artifact bundle

### Hard Gates

Hard gates include:

- `patch_applies`
- `compiles`
- `tests_pass`
- `schema_valid`
- `scope_pass`
- `safety_pass`
- `semantic_pass`
- `hidden_pass`
- `mutation_pass`

### Failure Tags

Failure tags are diagnostic categories. They allow HGP to distinguish format failures,
scope violations, semantic misses, runtime failures, concurrency issues, platform issues,
porting mismatches, agent-tool failures, and knowledge-graph failures.

### Repair Feedback

Repair feedback may include visible verifier output and public failure categories. It
must not reveal hidden verifier implementation details beyond what the benchmark chooses
to expose as repair feedback.

### Governance Cost

Governance cost is measured by repair attempts, timeout behavior, fallback use, and
eventually token/cost telemetry.

```text
first_pass      -> initial output trust
repaired_pass   -> recovery ability
repair_tax_rate -> governance cost
scope_control   -> maintainer safety
hidden_verifier -> regression safety
failure_tags    -> diagnostic feedback
```

## Result Metadata

Every result should record:

```json
{
  "generation_path": "direct | holon_auto | holon_workflow | holon_print | claw_cli",
  "governance_level": "blackbox_artifact | graybox_workspace | whitebox_native",
  "fallback_used": false,
  "workflow_attempted": true,
  "workflow_type": "artifact | graph_recall | none",
  "prompt_stack": null
}
```

`prompt_stack` is optional. It should be present only when the driver can honestly report
COPR unit IDs and versions.

## Driver Compatibility

| Driver | Expected HGP level |
| --- | --- |
| Direct model endpoint | HGP-L1 |
| Submitted human patch | HGP-L1 |
| Codex CLI | HGP-L2 |
| Claude Code | HGP-L2 |
| Antigravity CLI | HGP-L2 |
| Holon `--auto` | HGP-L2 |
| Holon workflow | HGP-L3 |

## MCP Relationship

MCP and HGP solve different problems.

```text
MCP = capability access
HGP = behavior governance
```

Holon may use MCP behind a CLI adapter, but HGP should evaluate the adapter's audited
inputs, outputs, workspace effects, and telemetry rather than exposing raw MCP schemas to
the model as uncontrolled context.

## Chain-of-Thought Policy

HGP-L3 requires decision provenance, not private chain-of-thought.

Allowed telemetry:

- prompt stack IDs
- selected context pack IDs
- tool calls
- validator results
- ledger deltas
- repair attempts
- artifact hashes

Not required:

- hidden reasoning text
- private model chain-of-thought

This keeps HGP compatible with local models, external APIs, and agents that intentionally
avoid exposing internal reasoning.
