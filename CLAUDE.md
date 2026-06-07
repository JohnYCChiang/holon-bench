# CLAUDE.md

## Role

You are working inside Holon-Bench.

This benchmark measures maintainer-style agent behavior: minimal patching, scope control, verifier-driven repair, hidden regression safety, and low repair cost.

Your goal is first-pass correctness, not impressive code.

Priority order:

1. pass on first attempt
2. stay inside allowed scope
3. preserve public behavior
4. avoid hidden regressions
5. minimize repair attempts

Small correct patches beat large clever rewrites.

## Operating Rules

Before editing, identify:

- the case goal
- allowed files
- forbidden or protected files
- visible verifier command
- smallest file set needed

Do not edit unrelated files.

Never modify benchmark metadata, schemas, verifiers, golden patches, reports, hidden/protected references, or tests unless the task explicitly asks for it.

Do not weaken tests, loosen validation, bypass checks, or change the benchmark to fit your patch.

## Patch Discipline

Make the smallest semantic change that satisfies the case.

Preserve:

- public APIs
- existing style
- deterministic output
- error semantics
- reference/parity behavior
- idempotency
- compatibility with current callers

Avoid:

- broad refactors
- new dependencies
- formatting unrelated files
- speculative architecture
- network access
- hidden reasoning dumps
- claiming success without running checks

## Verification

Run the most relevant verifier before finalizing.

Prefer case-provided verifier commands.

When no command is given, use the narrowest valid check:

- Python: targeted pytest or py_compile
- Rust: cargo test
- Go: go test ./...
- Dart/Flutter: dart test or flutter test
- repo checks: existing runners/check scripts

If verification fails, repair from the exact failure. Do not rewrite the whole solution.

## Hidden Regression Checklist

Before final answer, consider:

- empty input
- single item
- duplicates
- invalid input
- unicode / encoding
- bytes vs string
- timeout / cancellation
- deterministic ordering
- repeated execution
- path handling
- protected API compatibility

Do not overfit visible tests.

## Track Hints

Python: watch CLI behavior, subprocess output, JSON determinism, path handling, and importable API behavior.

Rust core: preserve trait contracts, Result semantics, ordering, bounds, and ownership clarity.

Rust porting: match the protected reference exactly. Do not edit the reference.

Go: watch nil vs empty slices, context cancellation, map ordering, interfaces, and error wrapping.

Game/server cases: preserve authoritative deterministic state. Never trust client input.

Flutter/Dart: keep logic testable and platform-neutral. Do not fix logic with UI-only changes.

Graph/memory cases: use only available evidence. Do not invent facts.

Repair cases: reproduce failure, find invariant, patch minimally, rerun verifier.

## Final Response Format

Use this shape only:

Summary:
- what changed

Verification:
- command: PASS
- command: FAIL, short reason
- Not run: reason

Changed files:
- path
