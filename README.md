# Holon Benchmark v0.1

Holon Benchmark measures model suitability inside Holon workflows, not generic
leaderboard coding strength.

The benchmark answers which local model should own which role:

- contract worker
- patch worker
- reviewer
- planner
- tool maker
- porting worker
- game system worker
- cross-platform app worker
- graph-aware workflow worker

## Layout

```text
manifest/   Benchmark, track, scoring, and failure taxonomy metadata.
cases/      Case manifests grouped by track.
fixtures/   Per-case fixture workspaces and protected parity oracles.
runners/    Deterministic runner, scorer, scope checker, and report tools.
schemas/    JSON schemas for cases, results, scores, and failures.
reports/    Generated benchmark output.
```

## Phase Plan

- Phase 1: 35 cases, 5 per track, to validate runner/scorer/report plumbing.
- Phase 2: 108 cases, 15 per original track plus 3 graph-memory workflow probes.
- Phase 3: 365 cases, full v0.1.
- Phase 4: mutation packs for scope traps, long-context noise, repair loops,
  security traps, and legacy debt traps.

The `graph_memory_workflow` track checks whether Holon can actually use project
knowledge during an agent run. Its fixtures seed `.holon/knowledge_seed.json`,
hide policy verifiers from model context, and require graph-only decisions to
pass.

See [ROADMAP.md](ROADMAP.md) for the next benchmark direction: repair-aware
scoring, hidden/mutation verifiers, DDD-first workflows, Holon self-bootstrap,
Zhenren Upsampler maintenance, and martial RPG simulation tracks.

## Quick Checks

```bash
python3 holon-bench/runners/schema_check.py holon-bench
python3 -m py_compile holon-bench/runners/*.py
```

## Direct Patch Benchmark

Generate a patch from an OpenAI-compatible local endpoint, then execute and
score it:

```bash
python3 holon-bench/runners/run_model_case.py py-tool-001 \
  --model qwen36-27b-mtp-q4 \
  --endpoint http://127.0.0.1:8086/v1 \
  --bench-root holon-bench

python3 holon-bench/runners/run_case.py py-tool-001 \
  --model qwen36-27b-mtp-q4 \
  --patch-file holon-bench/reports/qwen36-27b-mtp-q4_py-tool-001_patch.diff \
  --bench-root holon-bench
```

Run one complete track against a model endpoint:

```bash
python3 holon-bench/runners/run_track.py python_tool_engineering \
  --model qwen36-27b-mtp-q4 \
  --endpoint http://127.0.0.1:8086/v1 \
  --bench-root holon-bench
```

Use the Holon-style complete artifact protocol instead of strict unified diff:

```bash
python3 holon-bench/runners/run_track.py python_tool_engineering \
  --model qwen36-27b-mtp-q4 \
  --protocol artifact \
  --endpoint http://127.0.0.1:8086/v1 \
  --bench-root holon-bench
```

`rust_porting` fixtures keep a protected Python reference implementation and
verify Rust output against it during `cargo test`; semantic parity is therefore
a hard gate rather than a reviewer judgment.
