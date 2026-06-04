# OSS Maintainer Use Cases

This document explains why open-source maintainers should care about Holon-Bench, and how it helps you make informed decisions before trusting an AI coding agent with your repository.

---

## The Problem: You Don't Know What the Agent Will Break

When an AI coding agent submits a patch to your repository, several things can go wrong:

1. **Scope violation** — it modifies files it was not supposed to touch.
2. **Verifier blindness** — it passes your visible tests but breaks a hidden regression check.
3. **Repair failure** — it cannot recover from a failing test without human intervention.
4. **Excessive cost** — it repairs correctly, but only after burning 8 turns and thousands of tokens.
5. **Semantic drift** — it changes the visible interface of a protected API or parity contract.

These failures do not show up on generic coding benchmarks. They show up in production, after you've merged the PR.

Holon-Bench measures all five. Before you adopt Codex, Claude, Gemini, or any other agent for your OSS repository, run it through Holon-Bench and see the numbers.

---

## Scenario 1: Should I Trust This Agent to Auto-Merge Small PRs?

**Your situation**: You maintain an active OSS library. You're considering letting an agent auto-merge low-risk PRs (dependency bumps, minor refactors, doc fixes).

**What Holon-Bench tells you**:
- `first_pass` rate on `repair_needed` track — does it even understand broken fixtures?
- `scope_control` result — will it touch `setup.cfg` when you only asked it to fix a function?
- `hidden_verifier` result — does it pass your private regression suite, or just the visible CI?

**Recommended tracks to run**: `python_tool_engineering`, `repair_needed`

---

## Scenario 2: Should I Use This Agent for Rust→Go Porting Work?

**Your situation**: You are migrating a Rust crate to Go, or vice versa. You want to know if an agent can handle semantic parity, not just syntactic translation.

**What Holon-Bench tells you**:
- `rust_porting` track uses a protected Python reference implementation as a hard gate. The agent must produce Rust output that passes `cargo test` against that oracle — not just "looks correct".
- `go_core` and `rust_core` tracks measure correctness of idiomatic implementations.

**Recommended tracks to run**: `rust_porting`, `go_core`, `rust_core`

---

## Scenario 3: Is This Agent Safe for Flutter Cross-Platform Maintenance?

**Your situation**: Your app has iOS, Android, and web targets. You want to know if an agent will accidentally break one platform while fixing another.

**What Holon-Bench tells you**:
- `flutter_cross_platform` track fixtures include platform-specific constraints.
- `scope_control` checks prevent agents from silently modifying shared platform files.

**Recommended tracks to run**: `flutter_cross_platform`

---

## Scenario 4: How Expensive Is This Agent to Run in a Repair Loop?

**Your situation**: You're evaluating token cost vs. correctness tradeoffs between two models for your CI pipeline.

**What Holon-Bench tells you**:
- `repair_tax_rate` — average verifier-feedback turns per case.
- `avg_repair_attempts_to_pass` — among cases that eventually pass, how many turns did it take?
- Compare: a model with `first_pass=0.60, repair_tax=0.4` vs. `first_pass=0.45, repair_tax=1.8` — very different operating costs.

**Recommended tracks to run**: All tracks with `--repair-attempts 3`.

---

## Scenario 5: Graph-Aware Decisions and Knowledge Routing

**Your situation**: Your agent has access to project knowledge (a graph, a knowledge base, a context store). You want to know if it actually uses that knowledge or ignores it.

**What Holon-Bench tells you**:
- `graph_memory_workflow` track seeds `.holon/knowledge_seed.json` into the fixture workspace.
- Hidden verifiers check that the agent's decisions are consistent with the seeded knowledge — not random guesses.

**Recommended tracks to run**: `graph_memory_workflow`

---

## How to Run a Quick Safety Check Before Adopting an Agent

```bash
# 1. Clone this repo
git clone https://github.com/JohnYCChiang/holon-bench.git
cd holon-bench

# 2. Run schema check (no API key required)
python3 runners/schema_check.py .

# 3. Run selected cases from python_tool_engineering against your model endpoint
python3 runners/run_track.py python_tool_engineering \
  --model your-model-name \
  --endpoint http://your-endpoint/v1 \
  --bench-root . \
  --repair-attempts 3 \
  --case-ids py-tool-001,py-tool-009,py-tool-018,py-tool-041,py-tool-056

# 4. Read the report
cat reports/your-model-name_python_tool_engineering_report.json
```

See [`examples/`](../examples/) to learn how to add your own OSS repository as a custom track.
