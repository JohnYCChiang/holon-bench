"""Mutation runner (prereg M10 / task req 5).

The four mutations are transcribed from prereg A.4 — each MUST be *caught* by a
correct solution's laws/tests when injected:

  1. comparison flipped (``<`` -> ``<=``)
  2. capacity off-by-one
  3. uniqueness check dropped
  4. sortedness check dropped at one construction site

A mutation is applied to the *final solution* (not to the tests), the suite is
re-run, and the mutant is **killed iff >= 1 test fails** (task req 5). Two arm
mutators realise the prereg's AST-vs-source split:

* Baseline (Rust): a source patch (regex/literal transform on the impl source).
* Tao: an AST-level node swap on the agent's submitted def nodes (JSON).

An operator that cannot find its site reports ``applied=False`` ->
``not_applicable``. On a *correct* solution a not_applicable mutant is itself a
signal (the guard the mutation targets may be missing) and is surfaced as an
anomaly, never silently scored as "killed".

The kill decision delegates suite execution to a caller-provided runner so this
module stays a pure transform + orchestration layer.
"""

from __future__ import annotations

import copy
import re
from dataclasses import dataclass, field
from typing import Any, Callable


# --------------------------------------------------------------------------- specs

@dataclass
class MutationSpec:
    """One prereg-A.4 mutation, with a per-arm operator descriptor."""

    id: str
    name: str
    caught_by: list[str]                 # laws/properties expected to catch it
    rust: dict[str, Any]                 # baseline source-patch operator
    tao: dict[str, Any]                  # Tao AST node-swap operator
    #: an EQUIVALENT mutant — proven to leave the deliverable's observable output
    #: unchanged on all inputs, so it is unkillable BY CONSTRUCTION (not a suite
    #: gap). Excluded from kill-rate + critical-defects (standard mutation-testing
    #: practice). Set only with a recorded differential-equivalence proof.
    equivalent: bool = False


# Default operators. Patterns are deliberately tunable per run (a real solution's
# shape is unknown until submitted); the defaults target the canonical sites.
DEFAULT_SPECS: tuple[MutationSpec, ...] = (
    MutationSpec(
        id="MUT1", name="comparison-flipped", caught_by=["L-ord", "L-mem"],
        # space-delimited binary '<' only — never a generic such as Vec<i64>.
        rust={"op": "regex_sub", "pattern": r" < ", "repl": " <= ", "count": 1},
        tao={"op": "swap_def", "from_prim": "intLt", "to_prim": "intEq"},
    ),
    MutationSpec(
        id="MUT2", name="capacity-off-by-one", caught_by=["CAP", "L-size"],
        rust={"op": "regex_sub", "pattern": r"\b64\b", "repl": "65", "count": 1},
        tao={"op": "set_int", "find": 64, "repl": 65},
    ),
    MutationSpec(
        id="MUT3", name="uniqueness-check-dropped", caught_by=["L-idem", "L-size"],
        rust={"op": "regex_sub",
              "pattern": r"if\s+member\([^\n]*\n\s*return[^\n]*\n",
              "repl": "", "count": 1},
        tao={"op": "json_swap", "find_marker": "uniqueness-guard"},
    ),
    MutationSpec(
        id="MUT4", name="sortedness-check-dropped", caught_by=["L-ord", "L-comm"],
        rust={"op": "regex_sub", "pattern": r"\.sort\(\);?", "repl": "", "count": 1},
        tao={"op": "json_swap", "find_marker": "sortedness-guard"},
    ),
)


# Stage-1 mutations (prereg v1 A.4, relational mini-store). Each MUST be caught by
# a correct `report` solution's laws/tests. Rust patterns target canonical sites in
# the assembled rendition (join key equality, saturating add, the partition sort,
# the bound clamp) and are tunable per run; the Tao operators are AST node swaps on
# the submitted def nodes. Same applied=False => not_applicable discipline as v0.
STAGE1_SPECS: tuple[MutationSpec, ...] = (
    MutationSpec(
        id="S1-JOIN", name="join-key-flip", caught_by=["L-join"],
        # inner-join key equality `.id == ` -> `.id != ` (one site)
        rust={"op": "regex_sub", "pattern": r"\.id == ", "repl": ".id != ", "count": 1},
        tao={"op": "swap_def", "from_prim": "intEq", "to_prim": "intLt"},
    ),
    MutationSpec(
        id="S1-SUM", name="agg-identity-break", caught_by=["L-sum-bounded", "CAP"],
        # bounded accumulation: saturating_add -> saturating_sub
        rust={"op": "regex_sub", "pattern": r"saturating_add", "repl": "saturating_sub", "count": 1},
        tao={"op": "swap_def", "from_prim": "intAdd", "to_prim": "intEq"},
    ),
    # S1-GROUP / S1-BOUND are EQUIVALENT mutants for this task's `report` composition,
    # PROVEN by a 20k-input differential test (identical output signature; see
    # runs/tao-killtest-stage1/B2-baseline-mutation-equivalence.md):
    #  * S1-GROUP's `cs.dedup();` site is in `distinct_cats`, which `report` never
    #    calls (group_values uses index-sort grouping, no dedup) — off report's path.
    #  * S1-BOUND drops a clamp on `x.total` that `agg_sum_bounded` already bounds into
    #    [0,cap], and report inserts each cat once (no merge path) — redundant.
    # report's robust `sorted_unique_insert` (re-merge by cat + clamp) masks both
    # fault classes; the distinguishable faults are join-key (S1-JOIN) and sum-identity
    # (S1-SUM), both killed. Excluded from kill-rate/critical-defects, not silently.
    MutationSpec(
        id="S1-GROUP", name="group-partition-drop", caught_by=["L-group"], equivalent=True,
        rust={"op": "regex_sub", "pattern": r"\bcs\.dedup\(\);", "repl": "", "count": 1},
        tao={"op": "json_swap", "find_marker": "group-dedup-guard"},
    ),
    MutationSpec(
        id="S1-BOUND", name="bound-clamp-drop", caught_by=["L-sum-bounded", "L-sortuniq"],
        equivalent=True,
        rust={"op": "regex_sub", "pattern": r"row::clamp_total\(x\.total, cap\)",
              "repl": "x.total", "count": 1},
        tao={"op": "json_swap", "find_marker": "bound-clamp-guard"},
    ),
)


# pack_id -> mutation spec set. Keep DEFAULT_SPECS as the v0 default.
_SPECS_BY_PACK: dict[str, tuple[MutationSpec, ...]] = {
    "v0": DEFAULT_SPECS,
    "stage1": STAGE1_SPECS,
}


def specs_for(pack: str = "v0") -> tuple[MutationSpec, ...]:
    """Return the mutation spec set for a task pack ('v0' | 'stage1')."""
    if pack not in _SPECS_BY_PACK:
        raise ValueError(f"unknown mutation pack {pack!r} (have: {sorted(_SPECS_BY_PACK)})")
    return _SPECS_BY_PACK[pack]


# --------------------------------------------------------------------- rust mutator

@dataclass
class MutationOutcome:
    spec_id: str
    name: str
    applied: bool
    killed: bool | None          # None when not applied
    failed_tests: int = 0
    passed_tests: int = 0
    detail: str = ""
    equivalent: bool = False     # proven-equivalent mutant: excluded from scoring

    @property
    def status(self) -> str:
        if not self.applied:
            return "not_applicable"
        if self.equivalent:
            return "equivalent"
        return "killed" if self.killed else "survived"

    def to_dict(self) -> dict[str, Any]:
        return {
            "spec_id": self.spec_id, "name": self.name, "applied": self.applied,
            "status": self.status, "killed": self.killed, "equivalent": self.equivalent,
            "failed_tests": self.failed_tests, "passed_tests": self.passed_tests,
            "detail": self.detail,
        }


def apply_rust(source: str, op: dict[str, Any]) -> tuple[str, bool]:
    kind = op.get("op")
    if kind == "regex_sub":
        pattern = re.compile(op["pattern"], re.MULTILINE)
        if not pattern.search(source):
            return source, False
        mutated = pattern.sub(op["repl"], source, count=int(op.get("count", 1)))
        return mutated, mutated != source
    if kind == "literal_sub":
        find = op["find"]
        if find not in source:
            return source, False
        return source.replace(find, op["repl"], int(op.get("count", 1))), True
    raise ValueError(f"unknown rust mutation op {kind!r}")


def apply_tao(ast: Any, op: dict[str, Any], manifest: dict[str, Any]) -> tuple[Any, bool]:
    """Apply an AST-level node swap to a Tao def node (deep-copied)."""
    mutated = copy.deepcopy(ast)
    kind = op.get("op")
    if kind == "swap_def":
        prim = manifest.get("prim_defs", {})
        src_id = prim.get(op["from_prim"])
        dst_id = prim.get(op["to_prim"])
        if not src_id or not dst_id:
            return mutated, False
        changed = _replace_in_json(mutated, lambda v: v == src_id, dst_id)
        return mutated, changed
    if kind == "set_int":
        find, repl = int(op["find"]), int(op["repl"])
        changed = _replace_int_lit(mutated, find, repl)
        return mutated, changed
    if kind == "json_swap":
        find, repl = op.get("find"), op.get("replace")
        if find is None:
            return mutated, False
        changed = _replace_subtree(mutated, find, repl)
        return mutated, changed
    raise ValueError(f"unknown tao mutation op {kind!r}")


def _replace_in_json(node: Any, pred: Callable[[Any], bool], new: Any) -> bool:
    changed = False
    if isinstance(node, dict):
        for k, v in list(node.items()):
            if pred(v):
                node[k] = new
                changed = True
            elif _replace_in_json(v, pred, new):
                changed = True
    elif isinstance(node, list):
        for i, v in enumerate(node):
            if pred(v):
                node[i] = new
                changed = True
            elif _replace_in_json(v, pred, new):
                changed = True
    return changed


def _replace_int_lit(node: Any, find: int, repl: int) -> bool:
    changed = False
    if isinstance(node, dict):
        if set(node.keys()) == {"Int"} and node.get("Int") == find:
            node["Int"] = repl
            return True
        for v in node.values():
            if _replace_int_lit(v, find, repl):
                changed = True
    elif isinstance(node, list):
        for v in node:
            if _replace_int_lit(v, find, repl):
                changed = True
    return changed


def _replace_subtree(node: Any, find: Any, repl: Any) -> bool:
    changed = False
    if isinstance(node, dict):
        for k, v in list(node.items()):
            if v == find:
                node[k] = repl
                changed = True
            elif _replace_subtree(v, find, repl):
                changed = True
    elif isinstance(node, list):
        for i, v in enumerate(node):
            if v == find:
                node[i] = repl
                changed = True
            elif _replace_subtree(v, find, repl):
                changed = True
    return changed


# -------------------------------------------------------------------- orchestration

# A suite runner takes the mutated solution payload and returns {passed, failed}.
SuiteRunner = Callable[[Any], dict[str, int]]


def run_mutant(spec: MutationSpec, arm: str, solution: Any, *,
               manifest: dict[str, Any] | None, suite_runner: SuiteRunner) -> MutationOutcome:
    """Apply one mutation to ``solution`` and decide kill via ``suite_runner``."""
    if arm == "baseline":
        mutated, applied = apply_rust(solution, spec.rust)
    elif arm == "tao":
        mutated, applied = apply_tao(solution, spec.tao, manifest or {})
    else:
        raise ValueError(f"unknown arm {arm!r}")

    if not applied:
        return MutationOutcome(spec.id, spec.name, applied=False, killed=None,
                               detail="mutation site not found in final solution")
    res = suite_runner(mutated)
    failed = int(res.get("failed", 0))
    if spec.equivalent:
        # proven-equivalent mutant: it leaves observable output unchanged, so a
        # "survival" is expected and is NOT a suite gap. Recorded transparently and
        # excluded from kill-rate/critical-defects by the scorer.
        return MutationOutcome(
            spec.id, spec.name, applied=True, killed=failed > 0, equivalent=True,
            failed_tests=failed, passed_tests=int(res.get("passed", 0)),
            detail="EQUIVALENT mutant (proven; excluded) — output unchanged by construction")
    return MutationOutcome(
        spec.id, spec.name, applied=True, killed=failed > 0,
        failed_tests=failed, passed_tests=int(res.get("passed", 0)),
        detail="killed by suite" if failed > 0 else "SURVIVED — suite did not catch mutation",
    )


@dataclass
class MutationReport:
    arm: str
    outcomes: list[MutationOutcome] = field(default_factory=list)

    @property
    def kill_rate(self) -> float | None:
        applied = [o for o in self.outcomes if o.applied]
        if not applied:
            return None
        return sum(1 for o in applied if o.killed) / len(applied)

    @property
    def all_killed(self) -> bool:
        applied = [o for o in self.outcomes if o.applied]
        return bool(applied) and all(o.killed for o in applied)

    def to_dict(self) -> dict[str, Any]:
        return {
            "arm": self.arm,
            "kill_rate": self.kill_rate,
            "all_applied_killed": self.all_killed,
            "not_applicable": [o.spec_id for o in self.outcomes if not o.applied],
            "survivors": [o.spec_id for o in self.outcomes if o.applied and not o.killed],
            "outcomes": [o.to_dict() for o in self.outcomes],
        }
