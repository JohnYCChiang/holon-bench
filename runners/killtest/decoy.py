"""Decoy dry-run mode (spike plan P5 / task req 6).

A *different* toy task (NOT SortedUniqList) used to shake down the harness
mechanics. Decoy runs:
  * never touch the registered task or the acceptance/hidden suites;
  * never enter the experiment record — they write to a separate decoy log;
  * exercise the real instrumentation: live ``tao-port`` for the Tao arm, real
    ``cargo test`` + source-patch mutation for the baseline arm.

The toy task ("capped-push": push to a Vec until a cap of 64, count elements)
is chosen so the baseline mutation operators have real sites (a binary ``<`` and
the literal ``64``); the uniqueness/sortedness operators legitimately report
``not_applicable``, demonstrating that branch too.
"""

from __future__ import annotations

import json
import pathlib
import shutil
from typing import Any

from . import config, mutation, suites, templates
from .arms import ArmSession, now_ts
from .runlog import RunLog, RunHeader


DECOY_CARGO_TOML = """[package]
name = "killtest_decoy"
version = "0.0.0"
edition = "2021"

[lib]
path = "src/lib.rs"
"""

DECOY_LIB_RS = """//! Decoy toy task — capped push. NOT the registered task.
pub fn capped_push(v: &mut Vec<i64>, x: i64) {
    if (v.len() as i64) < 64 {
        v.push(x);
    }
}

pub fn count(v: &Vec<i64>) -> usize {
    v.len()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pushes_below_cap() {
        let mut v = Vec::new();
        for i in 0..3 {
            capped_push(&mut v, i);
        }
        assert_eq!(count(&v), 3);
    }

    #[test]
    fn respects_cap() {
        let mut v = Vec::new();
        for i in 0..100 {
            capped_push(&mut v, i);
        }
        assert_eq!(count(&v), 64);
    }
}
"""


def _decoy_provenance(paths: config.Paths) -> RunHeader:
    prov = config.Provenance.capture(paths)
    return RunHeader(
        run_id="decoy", arm="", model_id="decoy",
        harness_version_hash=prov.harness_version_sha256,
        toolchain_set_hash=prov.registry_sha256,
        suite_hashes={"note": "decoy uses no registered suite"}, decoy=True)


def run_baseline_decoy(paths: config.Paths, decoy_root: pathlib.Path) -> dict[str, Any]:
    """Full baseline pipeline on the toy task: scaffold → cargo test → mutation."""
    run_dir = decoy_root / "baseline"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    crate = run_dir / "crate"
    (crate / "src").mkdir(parents=True, exist_ok=True)
    (crate / "Cargo.toml").write_text(DECOY_CARGO_TOML, encoding="utf-8")
    impl_path = crate / "src" / "lib.rs"
    impl_path.write_text(DECOY_LIB_RS, encoding="utf-8")

    header = RunHeader(run_id="decoy-baseline", arm="baseline", model_id="decoy",
                       harness_version_hash="decoy", toolchain_set_hash="decoy",
                       suite_hashes={"decoy": True}, decoy=True)
    session = ArmSession(run_dir=run_dir, header=header)
    session.set_standing("decoy task brief", "decoy baseline mechanics")
    session.log.run_start(header, now_ts())

    # one accounted edit (the file write) + the verifier.
    session.record_file_write("src/lib.rs", impl_path.read_text(encoding="utf-8"))
    acc = session.run_baseline(crate, "cargo test --quiet", category="verifier")

    original = impl_path.read_text(encoding="utf-8")

    def suite_runner(mutated_source: str) -> dict[str, int]:
        impl_path.write_text(mutated_source, encoding="utf-8")
        try:
            proc_ok = session.run_baseline(crate, "cargo test --quiet",
                                           category="verifier").exit_code == 0
        finally:
            impl_path.write_text(original, encoding="utf-8")
        return {"passed": 1 if proc_ok else 0, "failed": 0 if proc_ok else 1}

    report = mutation.MutationReport(arm="baseline")
    for spec in mutation.DEFAULT_SPECS:
        report.outcomes.append(
            mutation.run_mutant(spec, "baseline", original, manifest=None,
                                suite_runner=suite_runner))

    score = {"green": acc.exit_code == 0, "mutation": report.to_dict()}
    session.log.score("decoy-baseline", "baseline", score, now_ts())
    session.finish("green" if acc.exit_code == 0 else "failed")
    return {"acceptance_green": acc.exit_code == 0,
            "mutation": report.to_dict(),
            "ledger": session.ledger.to_dict()}


def run_tao_decoy(paths: config.Paths, decoy_root: pathlib.Path) -> dict[str, Any]:
    """Live tao-port shakedown: init → trust → manifest → instantiate a prim-only
    law (exercises {prim:*} substitution) → txn-insert → test. No agent defs, so
    this never touches the registered task; it proves the Tao instrumentation."""
    if not paths.tao_port.exists():
        return {"skipped": True, "reason": f"tao-port binary not built at {paths.tao_port}"}

    run_dir = decoy_root / "tao"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    store = run_dir / ".tao"

    import subprocess
    init = subprocess.run([str(paths.tao_port), "init", "--store", str(store)],
                          text=True, capture_output=True, check=False)
    if init.returncode != 0:
        return {"skipped": True, "reason": f"tao init failed: {init.stderr}"}
    manifest = json.loads(init.stdout)

    # trust the SIGNED toolchain set from the registry (as the harness would).
    reg = json.loads(paths.registry.read_text(encoding="utf-8"))
    versions = [t["tool_version"] for t in reg["tools"].values()]
    subprocess.run([str(paths.tao_port), "trust", "--store", str(store),
                    "--as", "John", *versions], text=True, capture_output=True, check=False)

    header = RunHeader(run_id="decoy-tao", arm="tao", model_id="decoy",
                       harness_version_hash="decoy",
                       toolchain_set_hash=config.registry_hash(paths),
                       suite_hashes={"decoy": True}, decoy=True)
    session = ArmSession(run_dir=run_dir, header=header)
    session.set_standing("decoy task brief", "decoy tao mechanics")
    session.log.run_start(header, now_ts())

    # a prim-only law: Exec proposition  intEq 0 0  (true). Uses {prim:intEq}
    # so we exercise the template substitution path with the world manifest.
    law_template = {
        "schema_version": 0,
        "payload": {"Law": {
            "over": [],
            "stmt": {"App": [
                {"App": [{"Def": "{prim:intEq}"}, {"Lit": {"Int": 0}}]},
                {"Lit": {"Int": 0}},
            ]},
            "checker": "Exec",
        }},
    }
    mapping = {f"{{prim:{k}}}": v for k, v in manifest.get("prim_defs", {}).items()}
    law_node = templates.instantiate(law_template, mapping)

    # read a context bundle first (token-accounted context fetch), then edit+test.
    session.run_tao(paths, store, ["versions"])
    txn = {"inserts": [law_node], "vocab": [], "lexicon": [], "holes": [],
           "expects": [], "agent": "decoy"}
    receipt_res = session.run_tao(paths, store, ["txn"], stdin_text=json.dumps(txn))
    passed = None
    law_id = None
    if receipt_res.exit_code == 0:
        law_id = json.loads(receipt_res.stdout)["inserted"][-1]
        test_res = session.run_tao(paths, store, ["test", law_id])
        try:
            passed = json.loads(test_res.stdout).get("passed")
        except json.JSONDecodeError:
            passed = None

    score = {"prim_law_inserted": law_id is not None, "prim_law_passed": passed}
    session.log.score("decoy-tao", "tao", score, now_ts())
    session.finish("green" if passed else "failed")
    return {"law_inserted": law_id is not None, "law_passed": passed,
            "manifest_prims": len(manifest.get("prim_defs", {})),
            "ledger": session.ledger.to_dict()}


def run_decoy(paths: config.Paths, decoy_root: pathlib.Path | None = None) -> dict[str, Any]:
    decoy_root = decoy_root or (paths.run_root / "decoy")
    decoy_root.mkdir(parents=True, exist_ok=True)
    # guard: decoy root must not overlap the private suite.
    suites.assert_hidden_outside_mounts(paths, [decoy_root])
    out = {"baseline": run_baseline_decoy(paths, decoy_root),
           "tao": run_tao_decoy(paths, decoy_root),
           "decoy_root": str(decoy_root)}
    (decoy_root / "decoy_summary.json").write_text(
        json.dumps(out, indent=2, default=str), encoding="utf-8")
    return out
