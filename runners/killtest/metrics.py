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
from .tokens import median, percentile


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
    runs_counted: int = 0

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


def decide(tao: ArmMetrics, baseline: ArmMetrics) -> dict[str, Any]:
    """Apply R1-R5 and emit the §4 verdict. Mechanical; no judgement calls."""
    r1_ok, r1_d = _ratio_ok(tao.m1_median, baseline.m1_median, config.R1_MEDIAN_FACTOR)
    r2_ok, r2_d = _ratio_ok(tao.m2_p90, baseline.m2_p90, config.R2_P90_FACTOR)
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
