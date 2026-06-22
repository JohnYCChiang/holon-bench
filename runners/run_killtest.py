#!/usr/bin/env python3
"""Tao Stage 0 kill-test harness CLI (spike plan P4 / Appendix B).

Adapts Holon-Bench to run the FROZEN pre-registration in
``tao/docs/tao-killtest-prereg-v0.md``. Two arms (Tao port vs git+repo-map+Rust),
identical task brief, per-edit-cycle token accounting (M1/M2), append-only run
logging (incl. crashed/abandoned), template instantiation, mutation scoring
(M10), interleaved scheduling + arm-blind review packaging (M5), and a decoy
dry-run mode that never touches the registered task or suites.

This delivers the harness + run-log writer. It does NOT execute the real
SortedUniqList experiment: P5 shakedown / P6 runs start only after the pre-run
checklist passes AND the Legislator confirms (see ``checklist``).

Subcommands:
  hashes          compute suite hashes (G3 preparation)
  init-experiment stamp provenance + pinned params into the experiment log
  commit-suites   G3 witness: append suite hashes to the experiment log
  install-assets  copy acceptance rendition + docs into an arm mount; leak-scan
  leak-scan       scan arm-visible surfaces for hidden-suite fingerprints
  schedule        print the interleaved run plan
  checklist       evaluate the pre-run gate (prereg §7 / spike plan P5)
  start-run       create a per-run session (run_start + session.json)
  wrap            instrument one agent command into the run's token ledger
  score           score a run (acceptance / hidden+mutation M10)
  package-review  arm-blind M5 package of a run's final artifact
  record-review   record M5 review minutes (unseals the arm)
  report          compute the R1-R5 verdict across completed runs
  decoy           run the decoy shakedown (never enters the experiment record)
  selftest        offline self-test of the pure harness logic
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from killtest import (  # noqa: E402
    arms, checklist, config, decoy, metrics, mutation, schedule, scoring, suites, tokens,
)
from killtest.arms import ArmSession, now_ts  # noqa: E402
from killtest.runlog import RunLog, RunHeader  # noqa: E402


ASSET_DIR = pathlib.Path(__file__).resolve().parent / "killtest" / "assets"


def _emit(obj) -> None:
    print(json.dumps(obj, indent=2, default=str, sort_keys=True))


def _pack(args) -> config.TaskPack:
    return config.active_pack(getattr(args, "pack", None))


def _paths(args) -> config.Paths:
    return config.resolve_paths(
        run_root=getattr(args, "run_root", None),
        private_suite=getattr(args, "private_suite", None),
        pack=_pack(args))


def _experiment_log(paths: config.Paths, args) -> pathlib.Path:
    if getattr(args, "experiment_log", None):
        return pathlib.Path(args.experiment_log)
    return paths.run_root / "experiment.jsonl"


# --------------------------------------------------------------------- handlers

def cmd_hashes(args) -> int:
    paths = _paths(args)
    _emit(suites.compute_suite_hashes(paths))
    return 0


def cmd_init_experiment(args) -> int:
    paths = _paths(args)
    pack = _pack(args)
    log = RunLog(_experiment_log(paths, args))
    prov = config.Provenance.capture(paths)
    prov.extra["prereg_version"] = pack.prereg_version
    prov.prereg_version = pack.prereg_version
    params = {"n_per_arm": pack.n_per_arm, "cap": pack.cap,
              "reviewer": config.M5_REVIEWER, "arms": list(config.ARMS),
              "tokenizer": tokens.TOKENIZER_NAME, "pack": pack.pack_id,
              "metrics": [m.id for m in config.METRICS]}
    # record an approved model substitute (prereg v1.1 §5) so the checklist accepts
    # a non-pinned model_id while keeping both arms identical.
    if getattr(args, "substitute", None):
        params["approved_substitute"] = args.substitute
    log.experiment_init(model_id=args.model_id, provenance=prov.to_dict(),
                        params=params, ts=now_ts())
    _emit({"experiment_log": str(_experiment_log(paths, args)),
           "provenance": prov.to_dict(), "model_id": args.model_id, "pack": pack.pack_id})
    return 0


def cmd_commit_suites(args) -> int:
    paths = _paths(args)
    log = RunLog(_experiment_log(paths, args))
    hashes = suites.compute_suite_hashes(paths)
    log.suite_commit(hashes, witness=args.witness, ts=now_ts())
    _emit({"g3_committed": True, "witness": args.witness, "suite_hashes": hashes})
    return 0


def cmd_install_assets(args) -> int:
    paths = _paths(args)
    mount = pathlib.Path(args.mount)
    mount.mkdir(parents=True, exist_ok=True)
    suites.assert_hidden_outside_mounts(paths, [mount])
    installed = suites.install_acceptance_assets(paths, args.arm, mount)
    # standing docs (token-counted): task brief + arm mechanics.
    (mount / "task_brief.md").write_text(
        (ASSET_DIR / "task_brief.md").read_text(encoding="utf-8"), encoding="utf-8")
    mech = "tao_mechanics.md" if args.arm == "tao" else "baseline_mechanics.md"
    (mount / "mechanics.md").write_text(
        (ASSET_DIR / mech).read_text(encoding="utf-8"), encoding="utf-8")
    leak = suites.scan_for_leak([mount], suites.hidden_fingerprints(paths))
    if not leak.clean:
        _emit({"installed": installed, "leak": leak.to_dict()})
        return 1
    _emit({"arm": args.arm, "mount": str(mount), "installed_suite_files": installed,
           "standing_docs": ["task_brief.md", "mechanics.md"], "leak": leak.to_dict()})
    return 0


def cmd_leak_scan(args) -> int:
    paths = _paths(args)
    roots = [pathlib.Path(p) for p in args.roots]
    leak = suites.scan_for_leak(roots, suites.hidden_fingerprints(paths))
    _emit(leak.to_dict())
    return 0 if leak.clean else 1


def cmd_schedule(args) -> int:
    plan = schedule.build_schedule(args.n, seed=args.seed)
    _emit({"n_per_arm": args.n, "seed": args.seed,
           "plan": [s.to_dict() for s in plan]})
    return 0


def cmd_checklist(args) -> int:
    paths = _paths(args)
    pack = _pack(args)
    exp_log = _experiment_log(paths, args)
    # leak scan over all arm mounts + the experiment log.
    roots = [pathlib.Path(p) for p in (args.mounts or [])] + [exp_log]
    leak = suites.scan_for_leak(roots, suites.hidden_fingerprints(paths))
    result = checklist.run_checklist(paths, exp_log, leak.clean,
                                     n_per_arm=pack.n_per_arm,
                                     model_id_pinned=pack.model_id_pinned,
                                     model_substitutes=pack.model_substitutes)
    RunLog(exp_log).checklist(result["items"], gate_pass=result["gate_pass"], ts=now_ts())
    _emit(result)
    return 0 if result["gate_pass"] else 1


def cmd_start_run(args) -> int:
    paths = _paths(args)
    run_dir = pathlib.Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    prov = config.Provenance.capture(paths)
    hashes = suites.compute_suite_hashes(paths)
    header = RunHeader(
        run_id=args.run_id, arm=args.arm, model_id=args.model_id,
        harness_version_hash=prov.harness_version_sha256,
        toolchain_set_hash=prov.registry_sha256, suite_hashes=hashes)
    session = ArmSession(run_dir=run_dir, header=header)
    # standing context = task brief + arm mechanics doc (token-counted). Pack-aware:
    # a pack's assets live under assets/<pack_id>/ (v0 keeps them at the assets root).
    adir = ASSET_DIR / _pack(args).pack_id
    if not adir.exists():
        adir = ASSET_DIR
    brief = (adir / "task_brief.md").read_text(encoding="utf-8")
    mech_file = "tao_mechanics.md" if args.arm == "tao" else "baseline_mechanics.md"
    mech = (adir / mech_file).read_text(encoding="utf-8")
    # the provisioner writes a per-arm library index into the run dir (token-counted
    # standing context): tao = names+sigs+LAWS (bodies excluded); baseline = names+
    # sigs only (behaviour recovered by reading bodies). This is the full-survey
    # standing basis; the accounting models re-weight to faithful/amortized at report.
    extra: list[str] = []
    idx = run_dir / "library_index.md"
    if idx.exists():
        extra.append(idx.read_text(encoding="utf-8"))
    session.set_standing(brief, mech, *extra)
    session.log.run_start(header, now_ts())
    session.save()
    _emit({"run_id": args.run_id, "arm": args.arm, "run_dir": str(run_dir),
           "standing_tokens": session.ledger.standing_tokens})
    return 0


def cmd_wrap(args) -> int:
    paths = _paths(args)
    run_dir = pathlib.Path(args.run_dir)
    # argparse.REMAINDER keeps the literal `--` separator as command[0]; strip a
    # single leading `--` so `wrap ... -- cargo test` / `wrap ... -- manifest`
    # work as written instead of leaking `--` to the shell / tao-port (shakedown
    # finding: the leak produced spurious verifier roundtrips, inflating M4).
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    session = ArmSession.load(run_dir)
    if args.arm == "tao" or (session.header.arm == "tao" and args.arm is None):
        store = pathlib.Path(args.store) if args.store else run_dir / ".tao"
        stdin_text = sys.stdin.read() if args.stdin else None
        res = session.run_tao(paths, store, args.command, stdin_text=stdin_text)
    else:
        workdir = pathlib.Path(args.workdir or run_dir)
        if args.category == "edit" and args.file:
            # Baseline edit primitive: the written file *content* is what enters
            # the agent's context, so it is the edit cycle's M1/M2 token mass
            # (the intended protocol, per decoy.py's session.record_file_write).
            # Before this branch, cmd_wrap had no file-write path, so live
            # baseline edits degenerated to a marker cycle (~0 content tokens),
            # undercounting baseline M1/M2 vs the tao arm. record_file_write opens
            # a file_write cycle and tokenises the content as CAT_CONTEXT.
            target = workdir / args.file
            content = target.read_text(encoding="utf-8") if target.exists() else ""
            session.record_file_write(args.file, content)
            session.save()
            _emit({"exit_code": 0, "category": "edit", "accepted": True,
                   "is_diagnostic": False, "recorded_file": args.file,
                   "edit_tokens": tokens.count_tokens(content),
                   "roundtrips": session.roundtrips,
                   "edits_accepted": session.edits_accepted})
            return 0
        res = session.run_baseline(workdir, " ".join(args.command), category=args.category)
    session.save()
    _emit({"exit_code": res.exit_code, "category": res.category,
           "accepted": res.accepted, "is_diagnostic": res.is_diagnostic,
           "roundtrips": session.roundtrips, "edits_accepted": session.edits_accepted,
           "stdout": res.stdout, "stderr": res.stderr})
    return 0 if res.exit_code == 0 else res.exit_code


def cmd_finalize(args) -> int:
    """Close a run's still-open edit cycle and write run_end.

    Edit cycles are flushed to run.jsonl only when closed (the next edit, or
    finish()). A run's final cycle is otherwise left open in session.json and
    never reaches the run log — fatal for an arm whose whole solution is one edit
    (baseline: M1/M2 would see zero accepted edits). This is the missing
    end-of-run lifecycle step; run it once per run after the agent finishes,
    before report. Idempotent: a run with no open cycle just appends run_end."""
    run_dir = pathlib.Path(args.run_dir)
    session = ArmSession.load(run_dir)
    session.recording = True  # ensure the flush is recorded even if scoring left it off
    session.finish(args.outcome)
    _emit({"run_id": session.header.run_id, "arm": session.header.arm,
           "outcome": args.outcome, "edits_accepted": session.edits_accepted,
           "accepted_edit_cycles_flushed": True})
    return 0


def cmd_verify_acceptance(args) -> int:
    """Tao arm's black-box acceptance verifier (symmetric to baseline `cargo test`).

    Reads the agent's solution.json, instantiates + runs ONLY the acceptance suite
    via the shared scorer path (entry-marker + deep-subtree lifting handled
    internally), and reports green/pass/fail. The internal instantiation txns run
    with recording OFF — they are harness mechanics (like cargo's internal compile
    steps), not agent edits; the agent is charged ONE verifier entry for the result
    summary, exactly as the baseline arm is charged for cargo's output. This removes
    the run-00 asymmetry where the tao agent had to reverse-engineer scorer internals
    to self-verify. The hidden suite is never touched here."""
    paths = _paths(args)
    run_dir = pathlib.Path(args.run_dir)
    store = pathlib.Path(args.store) if args.store else run_dir / ".tao"
    session = ArmSession.load(run_dir)
    sol_path = pathlib.Path(args.solution) if args.solution else run_dir / "solution.json"
    if not sol_path.exists():
        _emit({"green": False, "error": f"solution.json not found: {sol_path}. "
               "Write your submitted def ids there first."})
        return 2
    solution = json.loads(sol_path.read_text(encoding="utf-8"))
    was = session.recording
    session.recording = False  # internal instantiation = mechanics, not agent edits
    # prefer the mount's own VISIBLE acceptance copy so the self-check works while
    # the private suite tree is relocated during the run window (integrity). Falls
    # back to the private suite (scoring time, post-restore).
    mount_acc = run_dir / "acceptance" / "tao"
    acc_dir = mount_acc if mount_acc.exists() else None
    try:
        detail = scoring.tao_acceptance_detail(session, paths, store, solution,
                                               acceptance_dir=acc_dir)
    finally:
        session.recording = was
    green = detail["failed"] == 0 and detail["passed"] > 0
    fails = [r["name"] for r in detail["results"] if not r["passed"]]
    summary = (f"acceptance: {detail['passed']} passed, {detail['failed']} failed"
               + (f"; failing: {', '.join(fails)}" if fails else ""))
    # charge ONE verifier entry for the summary the agent reads back.
    session.record(["verify-acceptance"], exit_code=0 if green else 3,
                   stdout=summary, stderr="", category="verifier",
                   accepted=False, is_diagnostic=not green)
    session.save()
    _emit({"green": green, "passed": detail["passed"], "failed": detail["failed"],
           "failing": fails, "summary": summary})
    return 0 if green else 3


def cmd_score(args) -> int:
    paths = _paths(args)
    specs = mutation.specs_for(_pack(args).mutation_specs)
    run_dir = pathlib.Path(args.run_dir)
    session = ArmSession.load(run_dir)
    if args.arm == "tao":
        store = pathlib.Path(args.store) if args.store else run_dir / ".tao"
        mount = pathlib.Path(args.mount or run_dir)
        score = scoring.tao_score(session, paths, store, mount, specs=specs)
    else:
        crate = pathlib.Path(args.crate or (run_dir / "crate"))
        hidden = paths.hidden_dir / "rust"
        score = scoring.baseline_score(session, paths, crate, hidden_rendition=hidden, specs=specs)
    session.log.score(session.header.run_id, args.arm, score, now_ts())
    session.save()
    _emit(score)
    return 0


def cmd_package_review(args) -> int:
    paths = _paths(args)
    review_root = pathlib.Path(args.review_root) if args.review_root else paths.run_root / "review"
    artifacts = [pathlib.Path(p) for p in args.artifacts]
    pkg = schedule.package_for_review(
        paths.run_root, run_id=args.run_id, arm=args.arm, artifact_paths=artifacts,
        review_root=review_root, seed=args.seed)
    # the response withholds the arm so it can be shown to the blind reviewer.
    _emit({"blind_id": pkg.blind_id, "package_dir": str(pkg.package_dir),
           "reviewer": config.M5_REVIEWER})
    return 0


def cmd_record_review(args) -> int:
    paths = _paths(args)
    review_root = pathlib.Path(args.review_root) if args.review_root else paths.run_root / "review"
    defects = json.loads(args.defects) if args.defects else []
    rec = schedule.ReviewRecord(blind_id=args.blind_id, minutes=args.minutes, defects=defects)
    resolved = rec.resolve_arm(review_root)  # unseals arm only after minutes are in
    log = RunLog(_experiment_log(paths, args))
    log.review(resolved["run_id"], resolved["arm"], minutes=resolved["minutes"],
               reviewer=resolved["reviewer"], blind=True, defects=resolved["defects"],
               ts=now_ts())
    _emit({"recorded": True, **resolved})
    return 0


def cmd_report(args) -> int:
    paths = _paths(args)
    # Per-run edit_cycle / verifier_roundtrip / score events live in each run's
    # own run.jsonl; review events live in the experiment log. Aggregate both so
    # the metrics see the full pool (cmd_report previously read only the
    # experiment log → runs_counted=0). Only real run-<NN>-<arm> dirs are pooled;
    # `*.shakedown` and other suffixes are excluded.
    records = RunLog(_experiment_log(paths, args)).read()
    for run_dir in sorted(paths.run_root.glob("run-*")):
        if not run_dir.is_dir():
            continue
        parts = run_dir.name.split("-")
        if len(parts) != 3 or parts[-1] not in config.ARMS:
            continue  # skip run-NN-arm.shakedown / decoy / other
        rj = run_dir / "run.jsonl"
        if rj.exists():
            records.extend(RunLog(rj).read())
    tao = metrics.metrics_from_runlog(records, "tao")
    base = metrics.metrics_from_runlog(records, "baseline")
    pack = _pack(args)
    # Stage1: the baseline's body-read cost (B3 / fork C) is added to baseline M1/M2
    # under two standards (measured-M8, conservative-full-survey). The BINDING verdict
    # uses the conservative survey. v0 has no separate body-read cost (supplement 0).
    survey_const = m8_measured = 0.0
    body_sens = None
    if pack.pack_id == "stage1":
        survey_const = _stage1_body_survey(paths)
        m8_measured = _stage1_m8_median(paths)
        body_sens = metrics.body_read_sensitivity(
            tao, base, m8_measured=m8_measured, survey_const=survey_const)
    verdict = metrics.decide(tao, base, baseline_m1_supplement=survey_const,
                             baseline_m2_supplement=survey_const)
    verdict["runs_counted"] = {"tao": tao.runs_counted, "baseline": base.runs_counted}
    if body_sens is not None:
        verdict["body_read_costs"] = {"conservative_full_survey": survey_const,
                                      "measured_M8_median": m8_measured}
        # The per-accepted-edit body-read sensitivity is ASYMMETRIC (it adds the
        # baseline's pre-edit body reads to M1 but not the tao arm's much larger
        # pre-edit grammar exploration + rejected-typecheck mass). Kept for reference
        # but DEMOTED — the binding token comparison is symmetric total-tokens below.
        body_sens["WARNING"] = ("asymmetric: adds baseline body-reads but not tao "
                                "exploration/iteration; use symmetric_total_tokens")
        verdict["body_read_sensitivity_reference_only"] = body_sens
        verdict["symmetric_total_tokens"] = _stage1_total_tokens(paths, m8_measured)
    # 3-row sensitivity table: R1/R2 under every accounting model (report all
    # three, don't cherry-pick). Observational; the binding verdict is `decide`.
    verdict["accounting_sensitivity"] = metrics.accounting_table(tao, base)
    verdict["pack"] = pack.pack_id
    _emit(verdict)
    return 0


def _stage1_body_survey(paths: config.Paths) -> float:
    """Conservative full-library body survey = count_tokens of the dependency module
    bodies the baseline must read (doc-comments stripped, as provisioned). Computed
    from the frozen reference lib.rs so it is grounded, not a magic constant."""
    import re
    lib_path = paths.private_suite / "rust" / "src" / "lib.rs"
    if not lib_path.exists():
        return 0.0
    text = lib_path.read_text(encoding="utf-8")
    text = "\n".join(ln for ln in text.splitlines() if not re.match(r"\s*//[/!]", ln))
    bodies = "\n".join(re.findall(r"pub mod \w+ \{.*?\n\}", text, re.S))
    return float(tokens.count_tokens(bodies))


def _stage1_total_tokens(paths: config.Paths, m8_measured: float) -> dict:
    """Symmetric total-tokens comparison: EVERYTHING each arm consumed to reach the
    accepted solution. tao = its wrapped-ledger total (standing + all reads + all
    iteration); baseline = its ledger total + the unwrapped body-read M8. This is the
    fair binding token comparison (both arms' pre-edit reads counted), unlike the
    per-accepted-edit M1 which drops them asymmetrically."""
    import statistics

    def totals(arm: str, supplement: float = 0.0) -> list[float]:
        out = []
        for rd in sorted(paths.run_root.glob(f"run-*-{arm}")):
            sj = rd / "session.json"
            if not sj.exists():
                continue
            led = json.loads(sj.read_text())["ledger"]
            tot = led["standing_tokens"] + sum(
                e["tokens"] for c in led["cycles"] for e in c["entries"]
                if "standing" not in e["label"])
            out.append(tot + supplement)
        return out
    tao_t = totals("tao")
    base_t = totals("baseline", m8_measured)
    if not tao_t or not base_t:
        return {"insufficient_data": True}
    tao_m, base_m = statistics.median(tao_t), statistics.median(base_t)
    r1 = tao_m <= config.R1_MEDIAN_FACTOR * base_m
    return {
        "tao_total_median": tao_m, "baseline_total_median": base_m,
        "ratio_tao_over_baseline": round(tao_m / base_m, 3) if base_m else None,
        "tao_cheaper": tao_m < base_m,
        "R1_token_rule_pass": r1,
        "tao_range": [min(tao_t), max(tao_t)], "baseline_range": [min(base_t), max(base_t)],
        "note": "binding token comparison; baseline includes measured body-read M8",
    }


def _stage1_m8_median(paths: config.Paths) -> float:
    """Median measured body-read tokens across baseline runs (m8.json sidecars written
    by the orchestration from each executor transcript). 0 if none recorded yet."""
    vals = []
    for run_dir in sorted(paths.run_root.glob("run-*-baseline")):
        m8f = run_dir / "m8.json"
        if m8f.exists():
            try:
                vals.append(float(json.loads(m8f.read_text())["m8_tokens"]))
            except Exception:
                pass
    if not vals:
        return 0.0
    vals.sort()
    n = len(vals)
    return vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2.0


def cmd_decoy(args) -> int:
    paths = _paths(args)
    root = pathlib.Path(args.decoy_root) if args.decoy_root else None
    _emit(decoy.run_decoy(paths, root))
    return 0


def cmd_selftest(args) -> int:
    from killtest import selftest
    ok = selftest.run()
    return 0 if ok else 1


# ------------------------------------------------------------------------ parser

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="run_killtest.py", description=__doc__.splitlines()[0])
    p.add_argument("--run-root", help="root for run artifacts (default ../runs/tao-killtest)")
    p.add_argument("--private-suite", help="path to the private suite (default ~/tao-killtest-private)")
    p.add_argument("--experiment-log", help="experiment JSONL path")
    p.add_argument("--pack", choices=sorted(config.PACKS), default=None,
                   help="task pack (default: env KILLTEST_PACK or v0)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("hashes", help="compute suite hashes").set_defaults(func=cmd_hashes)

    s = sub.add_parser("init-experiment", help="stamp provenance + params")
    s.add_argument("--model-id", default=config.MODEL_ID_PINNED)
    s.add_argument("--substitute", default=None,
                   help="approved model substitute recorded for this run (prereg v1.1 §5)")
    s.set_defaults(func=cmd_init_experiment)

    s = sub.add_parser("commit-suites", help="G3 witness: commit suite hashes")
    s.add_argument("--witness", default=config.M5_REVIEWER)
    s.set_defaults(func=cmd_commit_suites)

    s = sub.add_parser("install-assets", help="install acceptance + docs into an arm mount")
    s.add_argument("--arm", required=True, choices=config.ARMS)
    s.add_argument("--mount", required=True)
    s.set_defaults(func=cmd_install_assets)

    s = sub.add_parser("leak-scan", help="scan for hidden-suite leaks")
    s.add_argument("roots", nargs="+")
    s.set_defaults(func=cmd_leak_scan)

    s = sub.add_parser("schedule", help="print interleaved plan")
    s.add_argument("--n", type=int, default=config.N_PER_ARM)
    s.add_argument("--seed", type=int, default=0)
    s.set_defaults(func=cmd_schedule)

    s = sub.add_parser("checklist", help="evaluate the pre-run gate")
    s.add_argument("--mounts", nargs="*", help="arm mounts to leak-scan")
    s.set_defaults(func=cmd_checklist)

    s = sub.add_parser("start-run", help="create a per-run session")
    s.add_argument("--run-id", required=True)
    s.add_argument("--arm", required=True, choices=config.ARMS)
    s.add_argument("--run-dir", required=True)
    s.add_argument("--model-id", default=config.MODEL_ID_PINNED)
    s.set_defaults(func=cmd_start_run)

    s = sub.add_parser("wrap", help="instrument one agent command")
    s.add_argument("--run-dir", required=True)
    s.add_argument("--arm", choices=config.ARMS)
    s.add_argument("--store", help="tao store dir (tao arm)")
    s.add_argument("--workdir", help="working dir (baseline arm)")
    s.add_argument("--category", default="verifier",
                   choices=["edit", "verifier", "context", "query"])
    s.add_argument("--stdin", action="store_true", help="forward stdin to tao txn")
    s.add_argument("--file", help="baseline edit: path (rel to --workdir) whose "
                   "content is the edit cycle's context (M1/M2)")
    s.add_argument("command", nargs=argparse.REMAINDER)
    s.set_defaults(func=cmd_wrap)

    s = sub.add_parser("finalize", help="close the open edit cycle + write run_end (run once after the agent)")
    s.add_argument("--run-dir", required=True)
    s.add_argument("--outcome", default="green")
    s.set_defaults(func=cmd_finalize)

    s = sub.add_parser("verify-acceptance",
                       help="tao arm: black-box acceptance verifier (symmetric to cargo test)")
    s.add_argument("--run-dir", required=True)
    s.add_argument("--store")
    s.add_argument("--solution", help="path to solution.json (default <run-dir>/solution.json)")
    s.set_defaults(func=cmd_verify_acceptance)

    s = sub.add_parser("score", help="score a run")
    s.add_argument("--run-dir", required=True)
    s.add_argument("--arm", required=True, choices=config.ARMS)
    s.add_argument("--store")
    s.add_argument("--mount")
    s.add_argument("--crate")
    s.set_defaults(func=cmd_score)

    s = sub.add_parser("package-review", help="arm-blind M5 package")
    s.add_argument("--run-id", required=True)
    s.add_argument("--arm", required=True, choices=config.ARMS)
    s.add_argument("--review-root")
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("artifacts", nargs="+")
    s.set_defaults(func=cmd_package_review)

    s = sub.add_parser("record-review", help="record M5 minutes (unseals arm)")
    s.add_argument("--blind-id", required=True)
    s.add_argument("--minutes", type=float, required=True)
    s.add_argument("--review-root")
    s.add_argument("--defects", help="JSON list of {severity,...}")
    s.set_defaults(func=cmd_record_review)

    s = sub.add_parser("report", help="compute R1-R5 verdict")
    s.set_defaults(func=cmd_report)

    s = sub.add_parser("decoy", help="run decoy shakedown")
    s.add_argument("--decoy-root")
    s.set_defaults(func=cmd_decoy)

    sub.add_parser("selftest", help="offline self-test").set_defaults(func=cmd_selftest)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
