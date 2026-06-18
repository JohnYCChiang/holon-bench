# Handoff: holon-bench#16 - quantify fs governance comparison

Status: **completed after handoff**.

Claude Code implemented the bounded code change but could not create the
branch, validate, commit, or push because its command-approval gate denied
mutating and code-executing commands. Codex took over only the integration
steps: branch creation, validation, commit, push, PR, and merge handling.

## Target layer

holon-bench only. No `../holon` / `../tao` touched. No validators weakened.

## What changed

`runners/holon_fs_governance_smoke.py`:

1. Added `import report` (the runner already does `from common import
   bench_root`; `report` lives in the same `runners/` dir, so it resolves when
   the smoke runs as `python3 runners/holon_fs_governance_smoke.py .`).
2. After the existing three scenarios (ungoverned / governed-admit /
   governed-deny), the smoke feeds the three scores back through
   `report.build_governance_comparison(...)` — the *same* function `report.py`
   uses for a full benchmark run — and asserts the quantified result:
   - a comparison is produced and `matched_case_count == 1`;
   - the slice partitions into 1 ungoverned + 2 governed runs;
   - `ungoverned.governance_failure_count == 0`;
   - `governed.governance_failure_count == 1` and
     `cases_with_governance_failure == 1`;
   - `deltas.governance_failure_count == 1` (governed − ungoverned).
3. The final `ok` line prints the quantified delta and matched-case count.
4. Module docstring updated to describe the quantification step.

This turns the previously per-scenario pass/fail smoke into a single matched
**measurement**: governance surfaces exactly the one fs-write denial the
ungoverned baseline silently allowed (delta `+1`).

## Why this is the smallest backward-compatible measurement path

- Reuses existing `report.build_governance_comparison` /
  `governance_group_metrics`; **no new** schema, scoring field, tool class, or
  validator change.
- Reads only the *optional* governance fields already emitted by
  `score_case.py`; `build_governance_comparison` returns `None` when they are
  absent, so non-Holon / legacy results are unaffected (governance metadata
  stays optional).
- No `HOLON_BIN`, live model, or network — runs fully offline via the existing
  `holon_stub.py` witness model, like the pre-existing smoke.

## Expected metric values (derived by review of report.py grouping)

`metric_deltas` returns ints for integer metrics (`round(int-int,4)` → int), so
`:+d` formatting and `== 1` comparisons hold:
- governed group = [admit (0 failures), deny (1 failure)] → sum 1, case_count 2.
- ungoverned group = [ungoverned (0)] → sum 0, case_count 1.
- matched on `(track=python_tool_engineering, case_id=py-tool-001)` → 1 match.

## Validation

Run on branch `codex/bench/m8-fs-governance-comparison`:

- `python3 runners/schema_check.py .`
- `python3 -m py_compile runners/*.py`
- `python3 runners/docs_check.py .`
- `python3 runners/ci_smoke.py .`
- `python3 runners/holon_fs_governance_smoke.py .`
- `./scripts/check_world.sh` from the world root

## Risks

- If `report.build_governance_comparison` ever returns float deltas for
  `governance_failure_count`, the `:+d` format in the final print would need an
  `int(...)`; current `report.py` keeps it int.
