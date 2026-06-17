# Holon-Bench

[![CI](https://github.com/JohnYCChiang/holon-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/JohnYCChiang/holon-bench/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/JohnYCChiang/holon-bench?include_prereleases)](https://github.com/JohnYCChiang/holon-bench/releases)

**Holon-Bench is an open-source benchmark harness for evaluating AI coding agents on maintainer-style workflows: patch generation, repair loops, regression safety, scope control, verifier feedback, and multi-language repository maintenance.**

It measures whether an agent can do what a real maintainer cares about — not single-shot LeetCode-style answers, but the full cycle of:

- generating a correct patch on the first attempt (`first_pass`)
- reading verifier feedback and repairing its own work (`repaired_pass`)
- staying within the allowed file scope (`scope_pass`, summarized as scope control)
- passing hidden regression checks it cannot see (`hidden_pass`)
- converging without exhausting the repair budget (`repair_tax_rate`)

Holon is one private agent implementation that uses this benchmark. The benchmark harness itself is **agent-agnostic** — it works with any OpenAI-compatible endpoint, local model server, or API.

---

## Why OSS Maintainers Should Care

Before trusting an AI coding agent to touch your production repository, you should know:

- Will it modify files it was not supposed to touch?
- Can it recover from a failing test without human intervention?
- Does it respect your protected interfaces and parity contracts?
- How many repair attempts does it typically need, and at what token cost?

Holon-Bench answers these questions with **reproducible, structured, scored results** across Python, Rust, Go, and Flutter/Dart codebases.

See [`docs/oss-maintainer-use-cases.md`](docs/oss-maintainer-use-cases.md) for concrete scenarios.
See [`docs/agent-governance-ladder.md`](docs/agent-governance-ladder.md) for the driver capability model that keeps external CLI agents comparable without requiring Holon-native telemetry.
See [`docs/protocols/holon-governance-protocol.md`](docs/protocols/holon-governance-protocol.md) for the HGP v0.1 protocol contract.

---

## Tracks

| Track | Language | Focus |
|---|---|---|
| `python_tool_engineering` | Python | CLI tools, library APIs, test coverage |
| `rust_core` | Rust | Core library logic, trait implementations |
| `rust_bevy` | Rust | ECS game architecture, component systems |
| `rust_porting` | Rust / Python | Semantic parity porting with protected reference |
| `go_core` | Go | Standard library patterns, interfaces |
| `go_game_server` | Go | Authoritative server logic, simulation correctness |
| `flutter_cross_platform` | Dart / Flutter | Cross-platform widget and state correctness |
| `graph_memory_workflow` | Multi | Graph-aware agent decisions, knowledge routing |
| `repair_needed` | Multi | Pre-broken fixtures requiring diagnosis + repair |

---

## Layout

```text
manifest/        Benchmark, track, scoring, and failure taxonomy metadata.
cases/           Case manifests grouped by track (YAML).
fixtures/        Per-case fixture workspaces and protected parity oracles.
runners/         Deterministic runner, scorer, scope checker, and report tools.
schemas/         JSON schemas for cases, results, scores, and failures.
reports/         Generated benchmark output and baseline comparisons.
docs/            Guides for OSS maintainers and contributors.
examples/        Minimal runnable sample cases to onboard new contributors.
```

---

## Quick Start

### Schema and syntax check (no API key required)

```bash
python3 runners/schema_check.py .
python3 -m py_compile runners/*.py
python3 runners/docs_check.py .
python3 runners/ci_smoke.py .
python3 runners/holon_smoke.py .
python3 runners/holon_fs_governance_smoke.py .
```

`holon_smoke.py` runs one case end-to-end through the `holon-cli` driver with an
offline Holon stand-in (`runners/holon_stub.py`), so the Holon path — including
surfaced governance metadata — is exercised without a compiled Holon binary or
any remote API. Real Holon runs point the driver at the compiled binary via the
`HOLON_BIN` environment variable.

`holon_fs_governance_smoke.py` compares the same fs permission case across three
witness configurations — unconfigured (ungoverned, baseline allow), governed +
admit, and governed + deny — proving the behavioral difference the Tao
`EffectOp` witness gate introduces (holon#5 / tao#5) flows through the bench
end-to-end. The witness decision is modeled in the offline stub; see
`.claude/tasks/holon-tao-witness-gate.md` for what is measured and what remains
real-CLI wiring.

### Run a single case against any OpenAI-compatible endpoint

```bash
python3 runners/run_model_case.py py-tool-001 \
  --model <your-model-name> \
  --endpoint http://127.0.0.1:8086/v1 \
  --bench-root .

python3 runners/run_case.py py-tool-001 \
  --model <your-model-name> \
  --patch-file reports/<model>_py-tool-001_patch.diff \
  --bench-root .
```

### Run a full track

```bash
python3 runners/run_track.py python_tool_engineering \
  --model <your-model-name> \
  --endpoint http://127.0.0.1:8086/v1 \
  --repair-attempts 3 \
  --bench-root .
```

`--repair-attempts` is the canonical repair-loop flag. The deprecated
`--repair-budget` alias remains accepted for older automation.

### Holon-aligned generation controls

The direct driver exposes generation controls under the same vocabulary as Holon
workflow fields, so a model behaves consistently in the benchmark and inside Holon:

| Flag | Holon workflow field | Effect |
|---|---|---|
| `--max-output-tokens` | `max_output_tokens` | Sent as OpenAI-compatible `max_tokens` on the direct request; omitted when unset. |
| `--thinking-budget` | `thinking_budget` | Recorded in generation metadata. Not sent as a request field unless the endpoint convention already supports one. |
| `--generation-timeout-seconds` | — | Per-request generation timeout (default `600.0`). |

The deprecated `--generation-max-tokens` alias normalizes to `--max-output-tokens`.
`run_track.py` forwards all three to `run_model_case.py`.

```bash
python3 runners/run_track.py python_tool_engineering \
  --model <your-model-name> \
  --endpoint http://127.0.0.1:8086/v1 \
  --protocol artifact --driver direct \
  --max-output-tokens 4096 \
  --thinking-budget 768 \
  --generation-timeout-seconds 600 \
  --bench-root .
```

### Use artifact protocol instead of strict unified diff

```bash
python3 runners/run_track.py python_tool_engineering \
  --model <your-model-name> \
  --protocol artifact \
  --endpoint http://127.0.0.1:8086/v1 \
  --bench-root .
```

---

## Scoring Model

Each case produces core trust and repair metrics:

| Metric | Meaning |
|---|---|
| `first_pass` | Passes all hard gates on the initial submission |
| `repaired_pass` | Passes after verifier-feedback repair loop |
| `repair_attempts_used` | Number of repair turns consumed |
| `final_pass` | Passes all hard gates after the repair loop |
| `repair_tax_rate` | Aggregate repair attempts per benchmark case (cost signal) |
| `hidden_pass` | Hidden regression verifier passed when present |
| `mutation_pass` | Mutation verifier passed when present |

A model with low `first_pass` but high `repaired_pass` is expensive but recoverable. A model with high `repair_tax_rate` on one track signals that routing should allocate more token budget for that role.

---

## Phase Plan

- **Phase 1** — 48 cases: original mini core plus graph-memory and repair probes.
- **Phase 2** — 118 cases: compact core across all enabled tracks.
- **Phase 3** — 365 cases, full v0.1.
- **Phase 4** — Mutation packs: scope traps, long-context noise, repair loops, security traps, legacy debt traps.

---

## Baseline Results

See [`reports/baseline_summary.md`](reports/baseline_summary.md) for current model comparison results.

### External Agent Baselines

Holon-Bench is not tied to Holon or any single model backend. Current baselines include local OpenAI-compatible model servers and external CLI agents:

| Agent | Type | Governance level | Tracks evaluated |
|---|---|---|---|
| `antigravity-cli` | External CLI agent (Google) | L2 graybox workspace | `python_tool_engineering` (3/5 cases) |
| `codex` | External CLI agent (OpenAI) | L2 graybox workspace | pending |
| `Qwen3.6-35B-A3B-MTP-UD-Q8_K_XL` | Local OpenAI-compatible endpoint | L1 blackbox artifact | `python_tool_engineering`, `rust_porting`, `repair_needed` |
| `gemma-4-26B-A4B-it-UD-Q8_K_XL` | Local OpenAI-compatible endpoint | L1 blackbox artifact | `python_tool_engineering`, `rust_porting`, `repair_needed` |
| `holon-cli` | Holon-native workflow driver | L3 whitebox native | active development |

Antigravity CLI and Codex CLI are tracked as external-agent baselines to validate that Holon-Bench can evaluate CLI-based coding agents, not only local model endpoints. Holon-native runs may expose deeper process telemetry such as workflow type, generation path, knowledge-graph recall, and eventually COPR `prompt_stack`; external agents are still valid baselines when they only expose workspace diffs and artifacts.

---

## Adding Your Own Cases

See [`examples/`](examples/) for a minimal runnable case you can clone and adapt for your own OSS repository.

The `rust_porting` fixtures demonstrate the most advanced pattern: a protected Python reference implementation whose semantics are a hard gate for the Rust output via `cargo test`.

---

## Contributing

Issues and PRs welcome. See [`docs/oss-maintainer-use-cases.md`](docs/oss-maintainer-use-cases.md) for the design rationale.
