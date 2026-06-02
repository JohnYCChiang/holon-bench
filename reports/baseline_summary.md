# Baseline Results

This document summarizes benchmark results for evaluated models across Holon-Bench tracks.
Results are from Phase 1 (35 cases, 5 per track).

> **Note**: Results marked `—` indicate the track has not yet been run against this model.

---

## Summary Table

| Model | `py-tool` | `rs-core` | `rs-bevy` | `rs-port` | `go-core` | `go-game` | `flutter` | `graph` | `repair` | **Avg first_pass** |
|---|---|---|---|---|---|---|---|---|---|---|
| **antigravity-cli** (agent) | **3/5** | — | — | — | — | — | — | — | — | **0.60** |
| qwen36-27b-mtp-q4 (local) | 3/5 | — | — | 2/5 | — | — | — | — | 1/5 | **0.50** |
| gemma3-27b-q4 (local) | 2/5 | — | — | 1/5 | — | — | — | — | 0/5 | **0.33** |
| codex (API) | — | — | — | — | — | — | — | — | — | pending |

_Scores shown as `first_pass / total cases`._

> **Antigravity CLI baseline** is included as a non-Codex agent baseline to validate that Holon-Bench can evaluate external coding agents, not only local OpenAI-compatible endpoints. Codex baseline will be added when quota becomes available.

---

## Detailed: antigravity-cli — python_tool_engineering

_Antigravity CLI is Google's agentic development platform (successor to Gemini CLI). It is evaluated here as an external agent baseline to demonstrate Holon-Bench's agent-agnostic evaluation capability._

| Case | first_pass | repaired_pass | repair_attempts | result | notes |
|---|---|---|---|---|---|
| py-tool-001 | ✅ | — | 0 | **PASS** | Error enum struct on first attempt |
| py-tool-009 | — | — | — | pending | |
| py-tool-018 | ✅ | — | 1 (self) | **PASS** | First patch had bytes/str decode bug; self-repaired on verifier feedback |
| py-tool-027 | ✅ | — | 0 | **PASS** | Idempotent write with sort_keys determinism |
| py-tool-056 | — | — | — | pending | |

**first_pass rate**: 3/3 evaluated (pending 2 cases)
**repair_tax_rate**: 0.33 (1 self-repair turn across 3 cases)

### Repair Detail: py-tool-018

First attempt used `exc.stdout or ""` which returned `b'before\n'` (bytes) instead of `'before\n'` (str) — the `subprocess.TimeoutExpired` exception stores captured output as bytes even when `text=True` is set on the original `subprocess.run()` call. Verifier feedback identified the `AssertionError: b'before\n' != 'before\n'`. Second attempt added explicit bytes→str decode. **Repaired in 1 turn.**

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

## Reproducing Results

```bash
# Local model baseline
python3 runners/run_track.py python_tool_engineering \
  --model qwen36-27b-mtp-q4 \
  --endpoint http://127.0.0.1:8086/v1 \
  --bench-root . \
  --repair-budget 3

# Antigravity CLI baseline cases are in golden_patches/:
# golden_patches/py-tool-001.diff
# golden_patches/py-tool-018.diff
# golden_patches/py-tool-027.diff
```
