"""Per-run scoring: acceptance (green), hidden + mutation (M10), defects (M11).

Hidden-suite discipline: hidden tests are read at scoring time from outside every
arm mount and executed in a throwaway *scoring copy* of the solution — they are
never written into the arm-visible mount, so they cannot leak (task req 3).

The Tao path drives the live ``tao-port`` (txn-insert each instantiated law, then
``test`` it). The baseline path compiles the agent's crate and runs the rendition
suites with ``cargo test``. Both return a uniform per-run score dict consumed by
``metrics``.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
from typing import Any, Callable

from . import config, mutation, suites, templates
from .arms import ArmSession


# --------------------------------------------------------------------------- tao

def tao_manifest(paths: config.Paths, store: pathlib.Path) -> dict[str, Any]:
    proc = subprocess.run([str(paths.tao_port), "manifest", "--store", str(store)],
                          text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise SystemExit(f"tao manifest failed: {proc.stderr}")
    return json.loads(proc.stdout)


# P5/P6 shakedown finding: tao-port's txn JSON parser has a recursion limit
# (serde_json default 128), so deep App spines in instantiated law templates
# must be split into separate content-addressed Term nodes referenced via Def
# — the same graph-substitution the run-00 agent applied to its own laws.
# Scoring-path only; the substrate agents face is unchanged.

_DEPTH_LIMIT = 100
_LIFT_AT = 60
_TERM_KEYS = {"App", "Lam", "Let", "Lit", "Def", "Ctor", "Match", "Perform", "Hole", "Var"}


def _children(x: Any) -> list[Any]:
    if isinstance(x, dict):
        return list(x.values())
    if isinstance(x, list):
        return list(x)
    return []


def _depth(x: Any) -> int:
    # iterative post-order; hidden templates can be thousands of levels deep
    depth = 1
    stack = [(x, 1)]
    while stack:
        node, d = stack.pop()
        depth = max(depth, d)
        for c in _children(node):
            stack.append((c, d + 1))
    return depth


def _var_free(x: Any) -> bool:
    stack = [x]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if "Var" in node:
                return False
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return True


def _is_term(t: Any) -> bool:
    return (isinstance(t, dict) and len(t) == 1
            and next(iter(t)) in _TERM_KEYS
            and next(iter(t)) not in ("Lit", "Def", "Var", "Hole"))


def _insert_nodes(session: ArmSession, paths: config.Paths, store: pathlib.Path,
                  nodes: list[dict[str, Any]]) -> list[str]:
    txn = {"inserts": nodes, "vocab": [], "lexicon": [], "holes": [],
           "expects": [], "agent": "scorer"}
    res = session.run_tao(paths, store, ["txn"], stdin_text=json.dumps(txn))
    if res.exit_code != 0:
        raise SystemExit(f"law insert rejected: {res.stdout}{res.stderr}")
    receipt = json.loads(res.stdout)
    inserted = receipt.get("inserted") or []
    if len(inserted) < len(nodes):
        raise SystemExit(f"law insert returned too few ids: {receipt}")
    return inserted


def _split(session: ArmSession, paths: config.Paths, store: pathlib.Path, x: Any) -> Any:
    """Iteratively lift deep, closed (Var-free) term subtrees into separately
    inserted nodes (Def refs) until the tree fits the parser. Strategy: walk
    the max-depth child chain; lift the lowest liftable ancestor that still
    has ≥ _LIFT_AT depth below it. Each lift removes ≥ _LIFT_AT levels."""
    root = {"stmt": x}
    while True:
        total = _depth(root["stmt"])
        if total <= _DEPTH_LIMIT:
            return root["stmt"]
        # walk down the deepest chain, remembering liftable candidates
        path: list[tuple[Any, Any]] = []  # (container, key)
        node = root["stmt"]
        container, key = root, "stmt"
        best: tuple[Any, Any, Any] | None = None
        while True:
            d = _depth(node)
            if d <= _LIFT_AT:
                break
            if _is_term(node) and _var_free(node):
                best = (container, key, node)  # lowest-so-far liftable ancestor
            kids = []
            if isinstance(node, dict):
                kids = list(node.items())
            elif isinstance(node, list):
                kids = list(enumerate(node))
            if not kids:
                break
            ck, cv = max(kids, key=lambda kv: _depth(kv[1]))
            container, key, node = node, ck, cv
            path.append((container, key))
        if best is None:
            raise SystemExit("law template too deep even after closed-subtree lifting")
        b_container, b_key, b_node = best
        nid = _insert_deep_term(session, paths, store, b_node)
        b_container[b_key] = {"Def": nid}


def _insert_deep_term(session: ArmSession, paths: config.Paths, store: pathlib.Path,
                      term: Any) -> str:
    term = _split(session, paths, store, term)
    [nid] = _insert_nodes(session, paths, store,
                          [{"schema_version": 0, "payload": {"Term": term}}])
    return nid


_marker_cache: dict[str, str] = {}


def _entry_marker(session: ArmSession, paths: config.Paths, store: pathlib.Path,
                  entry_id: str) -> str:
    """Run-00 finding: vocab-entry ids in a Law over-clause fail at eval
    (over ids must resolve to Term nodes). Substitute a marker Term node,
    exactly as the agent's accepted workaround did."""
    if entry_id not in _marker_cache:
        [nid] = _insert_nodes(session, paths, store, [{
            "schema_version": 0,
            "payload": {"Term": {"Lit": {"Text": f"entry:{entry_id}"}}}}])
        _marker_cache[entry_id] = nid
    return _marker_cache[entry_id]


def tao_insert_law(session: ArmSession, paths: config.Paths, store: pathlib.Path,
                   law_node: dict[str, Any], entry_id: str | None = None) -> str:
    """Submit a law node as a txn insert; return its content-addressed id."""
    law = law_node.get("payload", {}).get("Law")
    if law is not None:
        law["stmt"] = _split(session, paths, store, law["stmt"])
        if entry_id and entry_id in (law.get("over") or []):
            m = _entry_marker(session, paths, store, entry_id)
            law["over"] = [m if o == entry_id else o for o in law["over"]]
    [nid] = _insert_nodes(session, paths, store, [law_node])
    return nid


def tao_test_law(session: ArmSession, paths: config.Paths, store: pathlib.Path,
                 law_id: str) -> bool:
    res = session.run_tao(paths, store, ["test", law_id])
    if res.exit_code == 2:
        return False  # diagnostic error
    try:
        return bool(json.loads(res.stdout).get("passed"))
    except json.JSONDecodeError:
        return False


def tao_run_suite(session: ArmSession, paths: config.Paths, store: pathlib.Path,
                  rendered: list[dict[str, Any]], entry_id: str | None = None) -> dict[str, int]:
    passed = failed = 0
    for item in rendered:
        law_id = tao_insert_law(session, paths, store, item["law"], entry_id=entry_id)
        if tao_test_law(session, paths, store, law_id):
            passed += 1
        else:
            failed += 1
    return {"passed": passed, "failed": failed}


def tao_acceptance_detail(session: ArmSession, paths: config.Paths, store: pathlib.Path,
                          solution: dict[str, Any]) -> dict[str, Any]:
    """Instantiate + run ONLY the acceptance suite against the agent's solution,
    returning per-test pass/fail. Shares the scorer's instantiation path
    (entry-marker + deep-subtree lifting) so the agent's black-box acceptance
    verifier (`verify-acceptance`) is identical to what scoring does — and so the
    agent never needs to know those mechanics. Touches the acceptance suite only;
    the hidden suite is never read here (no leak surface)."""
    manifest = tao_manifest(paths, store)
    mapping = templates.build_mapping(manifest, solution)
    eid = mapping.get("{EID}")
    acc = templates.render_suite_dir(paths.acceptance_dir / "tao", mapping)
    results: list[dict[str, Any]] = []
    for item in acc:
        law_id = tao_insert_law(session, paths, store, item["law"], entry_id=eid)
        ok = tao_test_law(session, paths, store, law_id)
        results.append({"name": item["name"], "passed": ok})
    passed = sum(1 for r in results if r["passed"])
    return {"passed": passed, "failed": len(results) - passed, "results": results}


def tao_score(session: ArmSession, paths: config.Paths, store: pathlib.Path,
              mount: pathlib.Path) -> dict[str, Any]:
    session.recording = False  # scorer commands are not agent activity
    manifest = tao_manifest(paths, store)
    solution = templates.load_solution(mount)
    mapping = templates.build_mapping(manifest, solution)

    eid = mapping.get("{EID}")
    acc = templates.render_suite_dir(paths.acceptance_dir / "tao", mapping)
    acc_res = tao_run_suite(session, paths, store, acc, entry_id=eid)

    # hidden read from outside the mount, executed against the live store.
    hidden = templates.render_suite_dir(paths.hidden_dir / "tao", mapping)
    hid_res = tao_run_suite(session, paths, store, hidden, entry_id=eid)

    # mutation: content addressing means a mutant is a NEW def id — laws must
    # be re-instantiated against it, never "re-run" against the original ids
    # (P6 shakedown finding: the original runner spuriously reported survival).
    def tao_suite_runner_factory(spec: mutation.MutationSpec) -> Callable[[Any], dict[str, int]]:
        def runner(mutated_def: Any) -> dict[str, int]:
            term = (mutated_def or {}).get("payload", {}).get("Term")
            if term is None:
                return {"passed": 0, "failed": 0}
            mut_id = _insert_deep_term(session, paths, store, term)
            mmap = dict(mapping)
            mmap["{INSERT}"] = mut_id
            acc_m = templates.render_suite_dir(paths.acceptance_dir / "tao", mmap)
            hid_m = templates.render_suite_dir(paths.hidden_dir / "tao", mmap)
            return tao_run_suite(session, paths, store, acc_m + hid_m, entry_id=eid)
        return runner

    mut_report = mutation.MutationReport(arm="tao")
    for spec in mutation.DEFAULT_SPECS:
        # fetch a target def to mutate (insert op AST) — best-effort by solution.
        target_id = solution.get("insert")
        node = _tao_node(paths, store, target_id) if target_id else None
        outcome = mutation.run_mutant(
            spec, "tao", node, manifest=manifest,
            suite_runner=tao_suite_runner_factory(spec))
        mut_report.outcomes.append(outcome)

    return _assemble_score("tao", acc_res, hid_res, mut_report,
                           accepted_edits=session.edits_accepted,
                           recoveries=session.recoveries)


def _tao_node(paths: config.Paths, store: pathlib.Path, node_id: str | None) -> Any:
    if not node_id:
        return None
    proc = subprocess.run([str(paths.tao_port), "node", "--store", str(store), node_id],
                          text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        return None
    return json.loads(proc.stdout)


# ----------------------------------------------------------------------- baseline

def baseline_score(session: ArmSession, paths: config.Paths, crate: pathlib.Path,
                   *, hidden_rendition: pathlib.Path, impl_rel: str = "src/lib.rs") -> dict[str, Any]:
    """Compile + run acceptance (in the mount) and hidden (in a scoring copy)."""
    session.recording = False  # scorer commands are not agent activity
    acc_res = _cargo_test(session, crate, category="verifier")

    # hidden suite executed in a throwaway copy so it never enters the mount.
    scoring_copy = crate.parent / (crate.name + "__scoring")
    if scoring_copy.exists():
        shutil.rmtree(scoring_copy)
    shutil.copytree(crate, scoring_copy)
    _install_hidden_tests(scoring_copy, hidden_rendition)
    hid = _cargo_test_raw(scoring_copy)
    hid_res = _parse_cargo(hid["stdout"] + hid["stderr"], 0 if hid["ok"] else 1)
    if hid_res["passed"] + hid_res["failed"] == 0:
        # compile failure or no parse: count as one failed run, honestly
        hid_res = {"passed": 0, "failed": 1}

    # mutation: source-patch the impl, re-run acceptance.
    impl_path = crate / impl_rel
    original = impl_path.read_text(encoding="utf-8")

    def baseline_suite_runner(mutated_source: str) -> dict[str, int]:
        impl_path.write_text(mutated_source, encoding="utf-8")
        try:
            r = _cargo_test_raw(crate)
        finally:
            impl_path.write_text(original, encoding="utf-8")
        return {"passed": 1 if r["ok"] else 0, "failed": 0 if r["ok"] else 1}

    mut_report = mutation.MutationReport(arm="baseline")
    for spec in mutation.DEFAULT_SPECS:
        outcome = mutation.run_mutant(spec, "baseline", original, manifest=None,
                                      suite_runner=baseline_suite_runner)
        mut_report.outcomes.append(outcome)

    shutil.rmtree(scoring_copy, ignore_errors=True)
    return _assemble_score("baseline", acc_res, hid_res, mut_report,
                           accepted_edits=session.edits_accepted,
                           recoveries=session.recoveries)


def _cargo_test(session: ArmSession, crate: pathlib.Path, *, category: str) -> dict[str, int]:
    res = session.run_baseline(crate, "cargo test --quiet", category=category)
    return _parse_cargo(res.stdout + res.stderr, res.exit_code)


def _cargo_test_raw(crate: pathlib.Path) -> dict[str, Any]:
    proc = subprocess.run("cargo test --quiet", cwd=str(crate), shell=True, text=True,
                          capture_output=True, check=False)
    return {"ok": proc.returncode == 0, "stdout": proc.stdout, "stderr": proc.stderr}


def _parse_cargo(output: str, exit_code: int) -> dict[str, int]:
    passed = failed = 0
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("test result:"):
            # e.g. "test result: ok. 10 passed; 0 failed; ..."
            for token, label in (("passed", "passed"), ("failed", "failed")):
                try:
                    idx = line.split(";")
                    for part in idx:
                        part = part.strip()
                        if part.endswith(label):
                            n = int(part.split()[0])
                            if label == "passed":
                                passed += n
                            else:
                                failed += n
                except (ValueError, IndexError):
                    pass
    if passed == 0 and failed == 0:
        # could not parse; fall back to exit code.
        return {"passed": 1 if exit_code == 0 else 0, "failed": 0 if exit_code == 0 else 1}
    return {"passed": passed, "failed": failed}


def _install_hidden_tests(crate: pathlib.Path, hidden_rendition: pathlib.Path) -> None:
    # P6 shakedown finding: the rendition is written as an in-crate module
    # (super:: paths), so install it next to the implementation like the
    # acceptance suite — an integration-test install fails to compile.
    src = hidden_rendition / "tests.rs"
    if src.exists():
        shutil.copy2(src, crate / "src" / "hidden_suite.rs")
        lib = crate / "src" / "lib.rs"
        text = lib.read_text(encoding="utf-8")
        if "mod hidden_suite;" not in text:
            lib.write_text(text + "\n#[cfg(test)]\nmod hidden_suite;\n", encoding="utf-8")


# ----------------------------------------------------------------------- assembly

def _assemble_score(arm: str, acc: dict[str, int], hidden: dict[str, int],
                    mut: mutation.MutationReport, *, accepted_edits: int,
                    recoveries: int) -> dict[str, Any]:
    green = acc["failed"] == 0 and acc["passed"] > 0
    # M10: pass rate on held-out (hidden) + mutation tests.
    hidden_total = hidden["passed"] + hidden["failed"]
    applied_muts = [o for o in mut.outcomes if o.applied]
    mut_killed = sum(1 for o in applied_muts if o.killed)
    m10_num = hidden["passed"] + mut_killed
    m10_den = hidden_total + len(applied_muts)
    m10_pass_rate = (m10_num / m10_den) if m10_den else None

    critical: list[dict[str, Any]] = []
    for o in mut.outcomes:
        if o.applied and not o.killed:
            # a surviving mutation = a logic error escaping the tests (M11 critical).
            critical.append({"mutation": o.spec_id, "name": o.name,
                             "severity": "logic-error-escaping-tests"})
    return {
        "arm": arm,
        "green": green,
        "acceptance": acc,
        "hidden": hidden,
        "mutation": mut.to_dict(),
        "m10_pass_rate": m10_pass_rate,
        "edits_to_green": accepted_edits if green else None,
        "recoveries": recoveries,
        "critical_defects": critical,
    }
