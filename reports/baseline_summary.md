# Baseline Results

This document summarizes benchmark results for evaluated models across Holon-Bench tracks.
Results are from Phase 1 (35 cases, 5 per track).

> **Note**: Results marked `—` indicate the track has not yet been run against this model.
> Baseline runs will be updated as evaluations are completed.

---

## Summary Table

| Model | `py-tool` | `rs-core` | `rs-bevy` | `rs-port` | `go-core` | `go-game` | `flutter` | `graph` | `repair` | **Avg first_pass** |
|---|---|---|---|---|---|---|---|---|---|---|
| qwen36-27b-mtp-q4 (local) | 3/5 | — | — | 2/5 | — | — | — | — | 1/5 | **0.50** |
| gemma3-27b-q4 (local) | 2/5 | — | — | 1/5 | — | — | — | — | 0/5 | **0.33** |
| codex (API) | — | — | — | — | — | — | — | — | — | TBD |

_Scores shown as `first_pass / total cases`._

---

## Detailed: qwen36-27b-mtp-q4 — python_tool_engineering

| Case | first_pass | repaired_pass | repair_attempts | result |
|---|---|---|---|---|
| py-tool-001 | ✅ | — | 0 | PASS |
| py-tool-009 | ✅ | — | 0 | PASS |
| py-tool-010 | ❌ | ✅ | 2 | REPAIRED |
| py-tool-018 | ✅ | — | 0 | PASS |
| py-tool-027 | ❌ | ❌ | 3 | FAIL |

**repair_tax_rate**: 1.0 (5 repair attempts / 5 cases)

---

## Detailed: qwen36-27b-mtp-q4 — rust_porting

| Case | first_pass | repaired_pass | repair_attempts | result |
|---|---|---|---|---|
| rs-port-001 | ✅ | — | 0 | PASS |
| rs-port-008 | ❌ | ✅ | 1 | REPAIRED |
| rs-port-016 | ❌ | ❌ | 3 | FAIL |
| rs-port-024 | ❌ | ❌ | 3 | FAIL |
| rs-port-045 | ✅ | — | 0 | PASS |

**repair_tax_rate**: 1.4 (7 repair attempts / 5 cases)

---

## Detailed: gemma3-27b-q4 — python_tool_engineering

| Case | first_pass | repaired_pass | repair_attempts | result |
|---|---|---|---|---|
| py-tool-001 | ✅ | — | 0 | PASS |
| py-tool-009 | ❌ | ✅ | 2 | REPAIRED |
| py-tool-010 | ❌ | ❌ | 3 | FAIL |
| py-tool-018 | ✅ | — | 0 | PASS |
| py-tool-027 | ❌ | ❌ | 3 | FAIL |

**repair_tax_rate**: 1.6 (8 repair attempts / 5 cases)

---

## How to Read These Numbers

- **first_pass** — The agent produced a passing patch on the first attempt, with no repair turns.
- **repaired_pass** — The agent failed initially but recovered after reading verifier feedback.
- **repair_tax_rate** — Total repair turns ÷ total cases. Lower is better. A rate above 2.0 on a track suggests that routing should allocate more token budget (or use a stronger model) for that role.
- **FAIL** — The agent did not pass even after exhausting the repair budget (default: 3 attempts).

---

## Reproducing These Results

```bash
python3 runners/run_track.py python_tool_engineering \
  --model qwen36-27b-mtp-q4 \
  --endpoint http://127.0.0.1:8086/v1 \
  --bench-root . \
  --repair-budget 3
```
