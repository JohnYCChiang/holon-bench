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
python3 runners/holon_fs_read_governance_smoke.py .
python3 runners/holon_real_fs_governance_smoke.py .
python3 runners/holon_fs_witness_kill_smoke.py .
python3 runners/holon_process_governance_smoke.py .
python3 runners/holon_governance_matrix.py .
python3 runners/holon_governance_matrix.py . --json
python3 runners/holon_governance_matrix.py . --out /tmp/holon-governance-matrix.json
python3 runners/holon_governance_matrix_kill_smoke.py .
python3 runners/holon_governance_matrix.py . --out /tmp/holon-governance-matrix.json
python3 runners/holon_governance_matrix_consume.py /tmp/holon-governance-matrix.json --require-ok
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

`holon_fs_read_governance_smoke.py` is the read-side sibling: it gates an fs
*read* (context exposure / information boundary) instead of a write, across the
same three witness configurations. tao#18 adds the fs-read tiers
`fs.stat | fs.list | fs.read` and holon#11 maps `read_file` / `grep_search` to
`fs.read` and `glob_search` to `fs.list` onto the same `tao.fsWitness` shape. A
read deny blocks the context exposure (no file contents surfaced) rather than a
mutation, but flows through the same scoring/comparison path and surfaces the
same governed-minus-ungoverned `+1` governance-failure delta over one matched
case.

`holon_real_fs_governance_smoke.py` is the opt-in real-binary version for Holon
commit `394a734` or newer. It writes real witness files and drives
`HOLON_TAO_FS_WITNESS=<path>` through the Holon CLI/settings surface added by
holon#7, checking unconfigured, governed-admit, and governed-deny/missing-grant
runs. It locates the binary via `HOLON_BIN` (wins), then the world-layout
`../holon/target/debug/holon`, then the legacy
`/home/taichi/Migration/holon/target/debug/holon`; diagnostics name every
candidate checked. With no usable binary **or** no endpoint configured it reports
`not-run` and exits 0 (use `--require-real` to make a skip nonzero) so default CI
stays offline. `HOLON_SMOKE_ENDPOINT` (or `--endpoint`) must match the provider
selected by the Holon smoke model: local OpenAI-compatible providers usually use a
base ending in one `/v1`, while Anthropic-style providers append `/v1/messages`
and usually expect a host-level base. A doubled path such as `/v1/v1/messages`
means the model/provider and base URL do not agree. An explicitly configured but
unreachable endpoint fails a clear preflight before the three-scenario run.
`--mock-endpoint` starts an in-process OpenAI-compatible mock so preflight passes
for deterministic local exercise of the offline stub (it is not guaranteed to
drive the real binary's fs write).

`holon_fs_witness_kill_smoke.py` is the fs witness governance **kill-readiness**
check: it stages a throwaway bench root (copying `runners/`, symlinking the rest
so tracked source is never mutated), injects each of four preregistered textual
regressions into the governance runtime — read deny still exposing context, the
read default EffectOp mapping to the wrong tier, write deny still editing, and
the governance comparison suppressing the failure count — and requires the
relevant fs governance smoke to *fail* on each. A mutant a smoke fails to catch
is reported as a survivor (nonzero exit, naming the mutant, target file, and
command that unexpectedly passed). This proves the smokes can fail, not just
pass; it is **not** the formal private Stage-1 Tao compression kill-test (see
`docs/killtest-stage1-readiness.md` and `runners/run_killtest.py`), which is a
frozen, arm-blind experiment over a private suite. This check is public,
offline, and scoped to the bench's own fs witness smoke surface.

`holon_process_governance_smoke.py` is the process-control sibling (M13c). Where
the fs smokes gate a write/read, this one gates a **modeled** process-control
action across the same three witness configurations. Tao/Holon landed the
process-control EffectOps `process.inspect | process.spawn | process.signal |
process.kill` and Holon gates selected process-control actions narrow-only; the
domain claim is the *liveness/ownership* of running processes, not filesystem
write/read exposure. The gated action is modeled only and entirely harmless — the
smoke never runs `kill` / `pkill` / `killall` / `ps` / `pgrep` or any command that
signals, inspects, or restarts a live process, and it never touches unrelated
running services. The offline stub models the witness decision under
`HOLON_STUB_PROCESS_WITNESS` (with `HOLON_STUB_PROCESS_OP` framing the named op)
and records the modeled action as an inert marker. A governed deny preserves
process liveness/ownership (the modeled action is blocked) and records a failing
`process_permission` check, surfacing the same governed-minus-ungoverned `+1`
governance-failure delta over one matched case.

`holon_governance_matrix.py` (M14) is **evidence aggregation, not a new
capability class**: it re-drives the three witness smokes above — `fs-write`
(filesystem mutation), `fs-read` (context exposure / information boundary), and
`process-control` (liveness/ownership of running processes) — and confirms each
still surfaces its expected governed-minus-ungoverned `+1` governance-failure
delta over one matched case. It emits a compact human summary, or a JSON matrix
with `--json` for world-health checks. The JSON is a stable machine-consumable
artifact contract carrying `schema_version: "governance-matrix/v1"` and a fixed
row shape, documented under `schemas/governance_matrix.schema.json`; `--out PATH`
writes that JSON artifact to a file (creating parent dirs) while leaving the
default human summary on stdout, and `--json --out PATH` both prints and writes
the same canonical JSON. It **fails closed**: any nonzero exit,
timeout, unparseable summary, or unexpected delta/matched-case count marks the
row (and the matrix) failed and exits nonzero — the exit code follows the matrix
verdict in every output mode, including when an artifact was written. The
aggregator only re-invokes the existing offline smokes via the Python
interpreter; it runs no live process-control command and the process-control row
stays stub-only.

`holon_governance_matrix_kill_smoke.py` (M16) is the matrix **kill-readiness**
check: the matrix's own tests prove it *passes* when the three smokes pass, but
not that it can *fail*. This smoke stages a throwaway bench root (copying
`runners/`, symlinking the rest), injects each of a set of preregistered textual
regressions, and requires the matrix to *fail* (nonzero) on each — a mutant the
matrix fails to catch is reported as a survivor. It covers two fault classes:
**evidence faults** that regress the underlying runtime (`report.py` /
`holon_stub.py`) so one smoke's real governance evidence drops, and **aggregation
faults** that drift the matrix's own row metadata or summary parsing
(`holon_governance_matrix.py`). Guard-*vacuity* (a check made unconditionally true)
is deliberately out of scope here — it produces no observable fault against good
smokes and is covered instead by the injected-`fake_runner` `FailClosedTest` in
`runners/test_holon_governance_matrix.py`. Like the fs witness kill smoke it is
public, offline, stub-only, and **not** the formal private Stage-1 Tao kill-test.
Its evidence-fault mutants now include a *per-row isolation* mutant for each of
fs-write, fs-read, and process-control: a regression confined to one capability
must fail the matrix via that capability's row alone (the other two rows still
pass), so each row's fail-closed path is proven load-bearing on its own and not
only by the global comparison mutant.

`holon_governance_matrix_consume.py` (M17) is the reusable consumer that gives the
M15 contract teeth. M15 froze the matrix output as `schema_version:
"governance-matrix/v1"` and stated consumers should reject any document whose
`schema_version` they do not recognize; this guard enforces exactly that. It loads
an artifact (e.g. one written with `--out`) and **fails closed** on an
unrecognized `schema_version` or a malformed envelope (missing required keys,
non-boolean `ok`, or `row_count` disagreeing with the actual rows). By default it
validates the contract envelope, not the verdict, so a well-formed `ok: false`
matrix is still a recognized document; `--require-ok` additionally requires `ok ==
true`, which is the mode world health uses. It is offline and pure — one JSON file
in, a pass/fail decision out, no smoke or subprocess.

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
