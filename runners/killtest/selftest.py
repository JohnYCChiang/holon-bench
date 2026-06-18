"""Offline self-test of the harness's pure logic.

No tao-port binary, no cargo — this validates the deterministic core so the
harness can be smoke-checked anywhere (CI). The live-binary / cargo paths are
exercised by the ``decoy`` command instead.
"""

from __future__ import annotations

import tempfile
import pathlib

from . import metrics, mutation, schedule, suites, templates, tokens
from .metrics import ArmMetrics


def _check(name: str, cond: bool, results: list[tuple[str, bool]]) -> None:
    results.append((name, bool(cond)))


def run() -> bool:
    results: list[tuple[str, bool]] = []

    # tokens: determinism + monotonicity.
    a = tokens.count_tokens("insert x (insert x s) = insert x s")
    b = tokens.count_tokens("insert x (insert x s) = insert x s")
    _check("token-determinism", a == b and a > 0, results)
    _check("token-empty", tokens.count_tokens("") == 0, results)

    # median / percentile.
    _check("median-odd", tokens.median([3, 1, 2]) == 2, results)
    _check("median-even", tokens.median([1, 2, 3, 4]) == 2.5, results)
    _check("p90", abs(tokens.percentile([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 90) - 9.1) < 1e-9, results)

    # ledger: standing context injected into every accepted cycle.
    led = tokens.TokenLedger()
    led.set_standing("a standing manual of some length")
    c1 = led.open_cycle("txn")
    c1.accepted = True
    c1.add(tokens.CAT_DIAGNOSTIC, "diag", "rejected: expected Int got Bool")
    c2 = led.open_cycle("txn")
    c2.accepted = True
    c2.add(tokens.CAT_CONTEXT, "bundle", "signatures only")
    pae = led.per_accepted_edit_tokens()
    _check("ledger-standing-each-cycle",
           all(t >= led.standing_tokens for t in pae) and len(pae) == 2, results)

    # template substitution: prims from manifest + agent def ids.
    manifest = {"prim_defs": {"intEq": "ID_INTEQ", "intLt": "ID_INTLT"}}
    solution = {"entry": "EID0", "empty": "E", "insert": "I", "member": "M", "size": "S"}
    mapping = templates.build_mapping(manifest, solution)
    tmpl = {"over": ["{EMPTY}", "{INSERT}"], "stmt": {"Def": "{prim:intEq}"},
            "eid": "{EID}", "lit": {"Int": 0}}
    inst = templates.instantiate(tmpl, mapping)
    _check("template-subst",
           inst["over"] == ["E", "I"] and inst["stmt"]["Def"] == "ID_INTEQ"
           and inst["eid"] == "EID0" and inst["lit"]["Int"] == 0, results)

    # unresolved placeholder must raise.
    try:
        templates.instantiate({"x": "{MISSING}"}, mapping)
        _check("template-unresolved-raises", False, results)
    except templates.SubstitutionError:
        _check("template-unresolved-raises", True, results)

    # rust mutation: comparison flip applies, generic untouched.
    src = "if (v.len() as i64) < 64 { v.push(x); }\nlet w: Vec<i64> = Vec::new();"
    mutated, applied = mutation.apply_rust(src, mutation.DEFAULT_SPECS[0].rust)
    _check("rust-cmp-flip", applied and "<= 64" in mutated and "Vec<i64>" in mutated, results)
    mutated2, applied2 = mutation.apply_rust(src, mutation.DEFAULT_SPECS[1].rust)
    _check("rust-cap-bump", applied2 and "65" in mutated2 and "i64" in mutated2, results)
    _, applied3 = mutation.apply_rust(src, mutation.DEFAULT_SPECS[3].rust)
    _check("rust-sort-not-applicable", not applied3, results)

    # tao mutation: swap_def + set_int.
    ast = {"App": [{"Def": "ID_INTLT"}, {"Lit": {"Int": 64}}]}
    sw, sok = mutation.apply_tao(ast, {"op": "swap_def", "from_prim": "intLt",
                                       "to_prim": "intEq"}, manifest)
    _check("tao-swap-def", sok and sw["App"][0]["Def"] == "ID_INTEQ", results)
    si, iok = mutation.apply_tao(ast, {"op": "set_int", "find": 64, "repl": 65}, manifest)
    _check("tao-set-int", iok and si["App"][1]["Lit"]["Int"] == 65, results)

    # mutation kill decision via fake suite runner.
    def killer(_m):
        return {"passed": 0, "failed": 1}

    out = mutation.run_mutant(mutation.DEFAULT_SPECS[0], "baseline", src,
                              manifest=None, suite_runner=killer)
    _check("mutation-killed", out.applied and out.killed and out.status == "killed", results)

    # decision rule: a PASS scenario.
    tao = ArmMetrics("tao", accepted_edit_tokens=[100, 110, 120],
                     m3_edits_to_green=[3, 3], m5_review_minutes=[5, 6],
                     m10_pass_rates=[1.0, 1.0])
    base = ArmMetrics("baseline", accepted_edit_tokens=[300, 320, 340],
                      m3_edits_to_green=[3, 3], m5_review_minutes=[6, 7],
                      m10_pass_rates=[1.0, 1.0])
    verdict = metrics.decide(tao, base)
    _check("decision-pass", verdict["verdict"] == "PASS", results)

    # decision rule: token win but correctness loss => cost relocation.
    base_bad = ArmMetrics("baseline", accepted_edit_tokens=[300, 320, 340],
                          m3_edits_to_green=[3, 3], m5_review_minutes=[6, 7],
                          m10_pass_rates=[1.0, 1.0])
    tao_bad = ArmMetrics("tao", accepted_edit_tokens=[100, 110, 120],
                         m3_edits_to_green=[3, 3], m5_review_minutes=[6, 7],
                         m10_pass_rates=[0.5, 0.5], m11_critical_defects=1)
    v2 = metrics.decide(tao_bad, base_bad)
    _check("decision-cost-relocation", v2["verdict"] == "FAIL (cost relocation)", results)

    # decision rule: token loss => falsified.
    tao_tok_loss = ArmMetrics("tao", accepted_edit_tokens=[290, 300, 310],
                              m3_edits_to_green=[3, 3], m5_review_minutes=[5, 6],
                              m10_pass_rates=[1.0, 1.0])
    v3 = metrics.decide(tao_tok_loss, base)
    _check("decision-falsified", v3["verdict"] == "FAIL (falsified)", results)

    # schedule: balanced interleave, both arms each pair.
    plan = schedule.build_schedule(5, seed=1)
    _check("schedule-count", len(plan) == 10, results)
    _check("schedule-balanced",
           sum(1 for s in plan if s.arm == "tao") == 5
           and sum(1 for s in plan if s.arm == "baseline") == 5, results)

    # M5 packaging: arm-blind package + sealed mapping resolves back to the arm.
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        art = root / "final.rs"
        art.write_text("pub fn empty() {}", encoding="utf-8")
        pkg = schedule.package_for_review(root, run_id="run-00-baseline", arm="baseline",
                                          artifact_paths=[art],
                                          review_root=root / "review", seed=3)
        blind_name_hides_arm = "baseline" not in pkg.package_dir.name and "tao" not in pkg.package_dir.name
        rec = schedule.ReviewRecord(blind_id=pkg.blind_id, minutes=4.5)
        resolved = rec.resolve_arm(root / "review")
        _check("m5-blind-package",
               blind_name_hides_arm and resolved["arm"] == "baseline"
               and resolved["minutes"] == 4.5, results)

    # leak scan: catches a planted fingerprint.
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        (root / "clean.txt").write_text("nothing secret here", encoding="utf-8")
        rep = suites.scan_for_leak([root], ["H07"])
        _check("leak-clean", rep.clean, results)
        (root / "leak.txt").write_text("oops H07 appears", encoding="utf-8")
        rep2 = suites.scan_for_leak([root], ["H07"])
        _check("leak-detected", not rep2.clean and len(rep2.hits) == 1, results)

    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    for name, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print(f"selftest: {passed}/{total} checks passed")
    return passed == total


if __name__ == "__main__":
    raise SystemExit(0 if run() else 1)
