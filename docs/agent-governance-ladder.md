# Agent Governance Ladder

Holon-Bench is an agent governance harness, not only a coding benchmark. It measures
whether an AI coding agent can be trusted under maintainer-style constraints:

- first-attempt reliability
- repairability from verifier feedback
- scope discipline
- hidden regression safety
- semantic correctness
- repair cost
- process traceability when available

The benchmark must remain usable with black-box external CLI agents while still allowing
Holon-native runs to expose deeper process telemetry. The solution is a three-level
governance ladder.

## L1: Blackbox Artifact

L1 evaluates the final submitted patch or artifact.

Compatible with:

- local OpenAI-compatible endpoints
- hosted model APIs
- any script that emits a patch or artifact
- human-written patches

Captured evidence:

- submission text
- patch or artifact apply result
- changed files after application
- public verifier output
- hidden verifier output
- mutation verifier output
- semantic checks
- failure taxonomy

Can evaluate:

- `first_pass`
- `repaired_pass`
- `repair_tax_rate`
- `scope_pass`
- `hidden_pass`
- `semantic_pass`

Cannot evaluate:

- internal tool choice
- prompt stack
- model routing
- context selection
- validator rejections before final output

L1 is result governance: the output is auditable even if the generation process is not.

## L2: Graybox Workspace

L2 runs an external CLI agent inside a temporary workspace and audits the workspace before
and after the run.

Compatible with:

- Codex CLI
- Claude Code
- Antigravity CLI
- Aider-like tools
- other noninteractive CLI coding agents

Captured evidence:

- stdout/stderr
- exit code
- timeout status
- git diff
- changed files
- generated artifacts, if any
- optional CLI-exported plans or reports

Can evaluate everything in L1, plus:

- workspace mutation behavior
- touched-file scope
- protected path mutation
- whether the agent produced expected artifacts
- coarse repair-loop cost

Cannot reliably evaluate:

- internal prompt stack
- exact context pack
- private tool trace
- internal planner state
- model routing decisions

L2 is workspace governance: the agent can be black-box internally, but its filesystem
behavior is externally auditable.

## L3: Whitebox Native

L3 is for Holon-native runs or any agent that exports compatible process telemetry.

Captured evidence:

- `prompt_stack`
- COPR unit IDs and versions
- workflow type
- generation path
- tool trace
- context pack IDs
- knowledge graph recall trace
- model route
- validator rejection reasons
- repair path
- ledger transitions
- rollback records

Can evaluate everything in L1 and L2, plus:

- whether the intended COPR stack was used
- whether a workflow state selected the right tools
- whether graph-memory recall was required and actually used
- whether process failures came from model behavior, prompt stack, runtime guard, or verifier design
- prompt/runtime effectiveness across cases

L3 is process governance: the agent is not only scored by outcome, but audited by how it
reached the outcome.

## Driver Capability Matrix

| Level | Driver class | Typical examples | Governance depth |
| --- | --- | --- | --- |
| L1 | `blackbox-artifact` | direct endpoint, submitted patch | Result only |
| L2 | `graybox-workspace` | Codex CLI, Claude Code, Antigravity CLI | Result + workspace behavior |
| L3 | `whitebox-native` | Holon workflow | Result + workspace + process telemetry |

The benchmark should never require all drivers to expose L3 telemetry. That would make it
less useful for comparing external agents. Instead, every run records its governance
level so reports do not compare black-box and white-box capabilities as if they exposed
the same evidence.

## Core Governance Metrics

```text
first_pass      -> initial output trust
repaired_pass   -> recovery ability
repair_tax_rate -> governance cost
scope_pass      -> maintainer safety
hidden_pass     -> regression safety
failure_tags    -> diagnostic feedback
```

`first_pass` is the trust signal. `repair_tax_rate` is the governance cost signal.

An agent with high final pass but low first pass, high repair tax, and frequent scope
violations is not broadly trustworthy; it is recoverable under strong supervision.

## Prompt Stack Telemetry

Whitebox-native runs should eventually record:

```json
{
  "prompt_stack": {
    "kernel": "holon_kernel_v1",
    "workflow": "minimal_patch_v1",
    "role": "patch_minimizer_v1",
    "recipe": ["bounded_context_intake_v1", "minimal_artifact_patch_v1"],
    "tips": ["avoid_extra_text_v1", "preserve_public_api_v1"],
    "output_contract": "artifact_files_only_v1"
  }
}
```

This lets reports correlate first-pass rate, repair tax, and failure tags with specific
COPR units. External drivers may leave `prompt_stack` empty or null.

## Reporting Rule

Reports should group or annotate results by governance level:

- L1 results prove output verifiability.
- L2 results prove workspace auditability.
- L3 results prove process traceability.

Comparing final pass rates across levels is allowed, but process-governance claims must
only be made for L3 runs.
