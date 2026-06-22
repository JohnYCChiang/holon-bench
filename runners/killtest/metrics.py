"""Metric computation (M1-M11) and the frozen decision rule (R1-R5).

The decision rule is transcribed verbatim from prereg §4 and is *closed*: no
metric is added or removed after the first run, and observational metrics cannot
affect the verdict (prereg §5). The verdict is mechanical — "no interpretation
step exists" (spike plan P6).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from . import config
from .tokens import (median, percentile, cycle_tokens_under_model,
                     ACCOUNTING_MODELS, CAT_STANDING)


@dataclass
class ArmMetrics:
    """Pooled metrics for one arm across its runs (prereg §3)."""

    arm: str
    # M1/M2 pool: every accepted-edit token total across all runs of this arm.
    accepted_edit_tokens: list[int] = field(default_factory=list)
    m3_edits_to_green: list[int] = field(default_factory=list)     # per run
    m4_roundtrips: list[int] = field(default_factory=list)         # per run
    m5_review_minutes: list[float] = field(default_factory=list)   # per run
    m9_recoveries: list[int] = field(default_factory=list)         # per run
    m10_pass_rates: list[float] = field(default_factory=list)      # per run (hidden+mutation)
    m11_critical_defects: int = 0                                  # count across runs
    # Observational, Tao-only (prereg §3 M6/M7/M8); colour the verdict, never feed it.
    m6_sig_bytes: list[int] = field(default_factory=list)          # signature thinness
    m7_sig_fraction: list[float] = field(default_factory=list)     # % bundle sigs vs bodies
    m8_body_fetches: list[int] = field(default_factory=list)       # body fetch count
    # Per accepted-edit component breakdowns, kept so M1/M2 can be recomputed under
    # each accounting model (the 3-row sensitivity table). (by_component, standing).
    accepted_components: list[dict[str, int]] = field(default_factory=list)
    accepted_standing: list[int] = field(default_factory=list)
    runs_counted: int = 0

    def model_edit_tokens(self, model_name: str) -> list[float]:
        """Per accepted-edit token totals recomputed under an accounting model."""
        n = len(self.accepted_components)
        return [cycle_tokens_under_model(bc, st, n, model_name)
                for bc, st in zip(self.accepted_components, self.accepted_standing)]

    def model_m1_m2(self, model_name: str) -> tuple[float | None, float | None]:
        vals = self.model_edit_tokens(model_name)
        return median(vals), percentile(vals, 90.0)

    @property
    def m1_median(self) -> float | None:
        return median([float(x) for x in self.accepted_edit_tokens])

    @property
    def m2_p90(self) -> float | None:
        return percentile([float(x) for x in self.accepted_edit_tokens], 90.0)

    @property
    def m3_median(self) -> float | None:
        return median([float(x) for x in self.m3_edits_to_green])

    @property
    def m5_median(self) -> float | None:
        return median(self.m5_review_minutes)

    @property
    def m10_mean_pass_rate(self) -> float | None:
        if not self.m10_pass_rates:
            return None
        return sum(self.m10_pass_rates) / len(self.m10_pass_rates)

    def to_dict(self) -> dict[str, Any]:
        return {
            "arm": self.arm,
            "runs_counted": self.runs_counted,
            "M1_median_tokens_per_accepted_edit": self.m1_median,
            "M2_p90_tokens_per_accepted_edit": self.m2_p90,
            "M3_median_edits_to_green": self.m3_median,
            "M4_roundtrips_per_run": self.m4_roundtrips,
            "M5_median_review_minutes": self.m5_median,
            "M9_recoveries_per_run": self.m9_recoveries,
            "M10_mean_pass_rate": self.m10_mean_pass_rate,
            "M11_critical_defects": self.m11_critical_defects,
            "accepted_edit_sample_size": len(self.accepted_edit_tokens),
            # observational (Tao-only); empty on the baseline arm.
            "M6_signature_bytes": self.m6_sig_bytes,
            "M7_signature_fraction": self.m7_sig_fraction,
            "M8_body_fetches": self.m8_body_fetches,
        }


def metrics_from_runlog(records: list[dict[str, Any]], arm: str) -> ArmMetrics:
    """Reconstruct an arm's pooled metrics from the append-only run log.

    M4 is counted from ``verifier_roundtrip`` events — from the log, never agent
    self-report (task req 8). Crashed/abandoned runs that never reached green are
    included in M3/M4 pools with their observed counts (prereg §5)."""
    am = ArmMetrics(arm=arm)
    # group per run_id.
    runs: dict[str, dict[str, Any]] = {}
    for r in records:
        if r.get("decoy"):
            continue
        run_id = r.get("run_id") or (r.get("run_id") if "run_id" in r else None)
        ev = r.get("event")
        if ev == "run_start" and r.get("arm") == arm and not r.get("decoy"):
            runs.setdefault(r["run_id"], _empty_run())
        if run_id is None or r.get("arm") not in (arm, None):
            continue
        if r.get("arm") != arm:
            continue
        bucket = runs.setdefault(run_id, _empty_run())
        if ev == "edit_cycle":
            cyc = r["cycle"]
            bucket["cycles"].append(cyc)
        elif ev == "verifier_roundtrip":
            bucket["roundtrips"] += 1
        elif ev == "score":
            bucket["score"] = r["score"]
        elif ev == "review":
            bucket["review_minutes"] = r.get("minutes")
            bucket["defects"] = r.get("defects", [])
        elif ev == "run_end":
            bucket["outcome"] = r.get("outcome")
            bucket["edits_accepted"] = r.get("edits_accepted")

    for run_id, b in runs.items():
        am.runs_counted += 1
        for cyc in b["cycles"]:
            if cyc.get("accepted") and cyc.get("survived", True):
                am.accepted_edit_tokens.append(int(cyc.get("tokens_total", 0)))
                bc = dict(cyc.get("tokens_by_component", {}))
                am.accepted_components.append(bc)
                am.accepted_standing.append(int(bc.get(CAT_STANDING, 0)))
        # M3 edits-to-green: accepted edits up to first green; if never green,
        # use total accepted edits as the observed (worst) count.
        score = b.get("score") or {}
        edits_to_green = score.get("edits_to_green")
        if edits_to_green is None:
            edits_to_green = b.get("edits_accepted")
        if edits_to_green is not None:
            am.m3_edits_to_green.append(int(edits_to_green))
        am.m4_roundtrips.append(int(b["roundtrips"]))
        if b.get("review_minutes") is not None:
            am.m5_review_minutes.append(float(b["review_minutes"]))
        if score.get("recoveries") is not None:
            am.m9_recoveries.append(int(score["recoveries"]))
        if score.get("m10_pass_rate") is not None:
            am.m10_pass_rates.append(float(score["m10_pass_rate"]))
        # observational M6/M7/M8 (Tao-only): recorded in the score when present.
        if score.get("m6_signature_bytes") is not None:
            am.m6_sig_bytes.append(int(score["m6_signature_bytes"]))
        if score.get("m7_signature_fraction") is not None:
            am.m7_sig_fraction.append(float(score["m7_signature_fraction"]))
        if score.get("m8_body_fetches") is not None:
            am.m8_body_fetches.append(int(score["m8_body_fetches"]))
        for d in b.get("defects", []) or []:
            if d.get("severity") in ("logic-error-escaping-tests", "invariant-violation"):
                am.m11_critical_defects += 1
        for d in (score.get("critical_defects") or []):
            am.m11_critical_defects += 1
    return am


def _empty_run() -> dict[str, Any]:
    return {"cycles": [], "roundtrips": 0, "score": None, "review_minutes": None,
            "defects": [], "outcome": None, "edits_accepted": None}


# ------------------------------------------------------------------- decision rule

@dataclass
class RuleResult:
    rule: str
    description: str
    passed: bool | None
    detail: str


def _ratio_ok(t: float | None, b: float | None, factor: float) -> tuple[bool | None, str]:
    if t is None or b is None:
        return None, f"insufficient data (tao={t}, baseline={b})"
    threshold = factor * b
    return t <= threshold, f"tao={t:.2f} <= {factor}*baseline={threshold:.2f}? (baseline={b:.2f})"


def _no_harm_ok(t: float | None, b: float | None) -> tuple[bool | None, str]:
    if t is None or b is None:
        return None, f"insufficient data (tao={t}, baseline={b})"
    allowed = b * (1.0 + config.NO_HARM_ALLOWANCE)
    return t <= allowed, (f"tao={t:.2f} <= baseline*{1 + config.NO_HARM_ALLOWANCE:.2f}"
                          f"={allowed:.2f}? (baseline={b:.2f})")


def decide(tao: ArmMetrics, baseline: ArmMetrics, *,
           baseline_m1_supplement: float = 0.0,
           baseline_m2_supplement: float = 0.0) -> dict[str, Any]:
    """Apply R1-R5 and emit the §4 verdict. Mechanical; no judgement calls.

    ``baseline_m{1,2}_supplement`` add the baseline arm's body-read cost (the tokens
    it spends reading dependency bodies to recover behaviour — absent from the wrapped
    ledger, see B3) to baseline M1/M2 before the R1/R2 ratio. Stage1 runs the verdict
    under two standards: measured-M8 and conservative-full-survey (binding). v0 passes
    0 (no separate body-read cost), so its behaviour is unchanged."""
    b_m1 = baseline.m1_median + baseline_m1_supplement if baseline.m1_median is not None else None
    b_m2 = baseline.m2_p90 + baseline_m2_supplement if baseline.m2_p90 is not None else None
    r1_ok, r1_d = _ratio_ok(tao.m1_median, b_m1, config.R1_MEDIAN_FACTOR)
    r2_ok, r2_d = _ratio_ok(tao.m2_p90, b_m2, config.R2_P90_FACTOR)
    r3_ok, r3_d = _no_harm_ok(tao.m3_median, baseline.m3_median)

    # R4: final correctness (M10 pass rate not worse; zero critical M11 defects).
    r4_ok: bool | None
    if tao.m10_mean_pass_rate is None or baseline.m10_mean_pass_rate is None:
        r4_ok, r4_d = None, "insufficient M10 data"
    else:
        not_worse = tao.m10_mean_pass_rate >= baseline.m10_mean_pass_rate - 1e-9
        no_critical = tao.m11_critical_defects == 0
        r4_ok = not_worse and no_critical
        r4_d = (f"M10 tao={tao.m10_mean_pass_rate:.3f} >= baseline="
                f"{baseline.m10_mean_pass_rate:.3f} and tao critical defects="
                f"{tao.m11_critical_defects}==0")
    r5_ok, r5_d = _no_harm_ok(tao.m5_median, baseline.m5_median)

    rules = [
        RuleResult("R1", "median(M1_T) <= 0.7 * median(M1_B)", r1_ok, r1_d),
        RuleResult("R2", "p90(M2_T) <= 0.8 * p90(M2_B)", r2_ok, r2_d),
        RuleResult("R3", "median(M3_T) not worse (<=110% baseline)", r3_ok, r3_d),
        RuleResult("R4", "M10 not worse and zero critical M11 defects", r4_ok, r4_d),
        RuleResult("R5", "median(M5_T) not worse (<=110% baseline)", r5_ok, r5_d),
    ]

    token_rules = [r1_ok, r2_ok]
    no_harm_rules = [r3_ok, r4_ok, r5_ok]

    if any(v is None for v in token_rules + no_harm_rules):
        verdict = "INCONCLUSIVE"
        reason = "one or more rules lack sufficient data (run count not reached / harness gap)"
    elif not all(token_rules):
        verdict = "FAIL (falsified)"
        reason = "compression claim dead: a token rule (R1/R2) failed (prereg §4, no partial credit)"
    elif all(token_rules) and not all(no_harm_rules):
        verdict = "FAIL (cost relocation)"
        reason = "tokens won but a no-harm rule (R3/R4/R5) failed: keystone assumption fails"
    elif all(token_rules) and all(no_harm_rules):
        verdict = "PASS"
        reason = "R1 .. R5 all hold: keystone assumption survives Stage 0 falsification"
    else:
        verdict = "INCONCLUSIVE"
        reason = "unreachable combination"

    return {
        "verdict": verdict,
        "reason": reason,
        "rules": [{"rule": r.rule, "description": r.description,
                   "passed": r.passed, "detail": r.detail} for r in rules],
        "tao": tao.to_dict(),
        "baseline": baseline.to_dict(),
        "thresholds": {
            "R1_median_factor": config.R1_MEDIAN_FACTOR,
            "R2_p90_factor": config.R2_P90_FACTOR,
            "no_harm_allowance": config.NO_HARM_ALLOWANCE,
        },
        "prereg_version": config.PREREG_VERSION,
    }


def body_read_sensitivity(tao: ArmMetrics, baseline: ArmMetrics, *,
                          m8_measured: float, survey_const: float) -> dict[str, Any]:
    """Stage1 fork-C: the R1/R2 verdict under TWO body-read standards added to the
    baseline's M1/M2 (the cost it spends reading dependency bodies — see B3):
      * measured_M8           — what the real executor actually read (transcript).
      * conservative_full_survey — the full library body survey (BINDING; an
                                   undocumented library is realistically surveyed).
    The tao arm carries laws in its standing context, so no body-read term is added."""
    standards = [("measured_M8", m8_measured),
                 ("conservative_full_survey", survey_const)]
    rows = []
    for name, supp in standards:
        v = decide(tao, baseline, baseline_m1_supplement=supp, baseline_m2_supplement=supp)
        by_rule = {r["rule"]: r for r in v["rules"]}
        rows.append({
            "standard": name, "baseline_body_read_tokens": supp,
            "M1_tao": tao.m1_median,
            "M1_baseline_with_reads": (baseline.m1_median + supp)
                if baseline.m1_median is not None else None,
            "R1_pass": by_rule["R1"]["passed"], "R1_detail": by_rule["R1"]["detail"],
            "R2_pass": by_rule["R2"]["passed"], "R2_detail": by_rule["R2"]["detail"],
            "verdict": v["verdict"],
        })
    return {"binding_standard": "conservative_full_survey",
            "note": "M1_baseline = wrapped-ledger M1 + body-read cost; tao laws are in "
                    "standing (no body-read term). See B3.",
            "standards": rows}


def accounting_table(tao: ArmMetrics, baseline: ArmMetrics, *,
                     r1_factor: float = config.R1_MEDIAN_FACTOR,
                     r2_factor: float = config.R2_P90_FACTOR) -> dict[str, Any]:
    """The token rules R1/R2 recomputed under EVERY accounting model — the
    3-row sensitivity table the Stage-1 verdict must report (run all three, do
    not cherry-pick). Observational framing only; the binding verdict stays the
    single prereg accounting in ``decide``."""
    rows = []
    for name in ACCOUNTING_MODELS:
        t1, t2 = tao.model_m1_m2(name)
        b1, b2 = baseline.model_m1_m2(name)
        r1_ok, r1_d = _ratio_ok(t1, b1, r1_factor)
        r2_ok, r2_d = _ratio_ok(t2, b2, r2_factor)
        rows.append({
            "accounting_model": name,
            "standing": ACCOUNTING_MODELS[name]["standing"],
            "M1_tao": t1, "M1_baseline": b1, "R1_pass": r1_ok, "R1_detail": r1_d,
            "M2_tao": t2, "M2_baseline": b2, "R2_pass": r2_ok, "R2_detail": r2_d,
        })
    return {"r1_factor": r1_factor, "r2_factor": r2_factor, "rows": rows}
