# Benchmark Modes: Deterministic Baseline vs. Sampling-Profile Sweep

Holon-Bench measures maintainer-style agent behavior. For local models that
behavior depends on **sampling parameters**, not just the model weights. A model
that looks weak at one temperature can be strong at another, and a borderline case
can flip pass/fail run-to-run when sampling is stochastic. Holon-Bench therefore
supports two complementary evaluation modes.

The direct driver exposes the sampling controls as canonical flags on both
`run_model_case.py` and `run_track.py`:

| Flag | OpenAI-compatible field | Default | Notes |
|---|---|---|---|
| `--temperature` | `temperature` | `0.1` | `0` = greedy (deterministic decode). |
| `--top-p` | `top_p` | `0.9` | Nucleus sampling cutoff. |
| `--min-p` | `min_p` | unset | Sent **only when provided**; some endpoints do not accept it. |

All three are recorded in the per-generation metadata (`temperature`, `top_p`,
`min_p`) alongside the existing token telemetry (`completion_tokens`,
`finish_reason`, `truncated`), so every result is self-describing.

---

## Mode 1 — Deterministic Baseline

Goal: a **reproducible** number you can compare across model versions and over
time. Use greedy decoding so the same case produces the same artifact every run.

```bash
python3 runners/run_track.py python_tool_engineering \
  --model <your-model-name> \
  --endpoint http://127.0.0.1:8080/v1 \
  --protocol artifact --driver direct \
  --temperature 0 --top-p 1 --min-p 0 \
  --repair-attempts 3 \
  --max-output-tokens 4096 --thinking-budget 768 --generation-timeout-seconds 600 \
  --bench-root .
```

Notes:
- Greedy removes sampling noise, but GPU/quantized-KV kernels can still introduce
  small non-determinism on some backends. Treat the baseline as low-variance, not
  bit-exact.
- This is the right mode for regression tracking and routing decisions
  (`minimum_cases_for_routing`, `minimum_hard_pass_rate_for_routing`).

## Mode 2 — Exploratory Sampling-Profile Sweep

Goal: discover a model's **capability envelope** — how pass rate, repair tax,
truncation, and rambling vary with sampling. Run several named profiles, each
repeated `runs_per_case` times, and read distributions rather than single points.

Reference profiles:

| Profile | temperature | top_p | min_p |
|---|---|---|---|
| greedy | 0 | 1 | 0 |
| conservative | 0.1 | 0.9 | 0 |
| current | 0.2 | 0.9 | 0 |
| balanced | 0.6 | 0.95 | 0.05 |
| high-explore | 1.0 | 0.95 | 0.1 |
| unsloth-style-high | 1.5 | 0.95 | 0.1 |
| high-temp-no-minp | 1.5 | 0.95 | 0 |

Each profile is one `run_track.py` invocation per repeat, e.g. the `balanced`
profile:

```bash
python3 runners/run_track.py python_tool_engineering \
  --model <your-model-name> \
  --endpoint http://127.0.0.1:8080/v1 \
  --protocol artifact --driver direct \
  --case-ids py-tool-001,py-tool-018 \
  --temperature 0.6 --top-p 0.95 --min-p 0.05 \
  --repair-attempts 3 \
  --max-output-tokens 4096 --thinking-budget 768 --generation-timeout-seconds 600 \
  --bench-root .
```

Metrics to aggregate across repeats per (profile, case):
- `first_pass_rate`, `repaired_pass_rate`, `final_pass_rate`
- `repair_tax_mean` (mean `repair_attempts_used`)
- `truncation_rate` (fraction of generations with `finish_reason == "length"`)
- ramble/repetition failures (truncated AND failed — high-`min_p`=0 high-temp
  profiles are the usual offenders)
- artifact extraction success rate
- dominant failure tags
- token distribution (`completion_tokens`)

Because higher temperatures increase variance, **always report sweep results as
rates over `runs_per_case`**, never as a single run. Sweep mode is for
exploration and tuning; promote a chosen profile to deterministic baseline mode
for the official number.

### Reproducibility caveat

The local llama.cpp server is a persistent process; its RNG state carries across
requests, so even fixed-seed sampling is not reproducible request-to-request
unless `--temperature 0`. This is exactly why borderline cases flip between runs
and why sweep metrics must be rates.
