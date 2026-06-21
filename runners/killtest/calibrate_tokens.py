#!/usr/bin/env python3
"""A1-adjacent instrument calibration for the kill-test token metric (M1/M2).

The verdict (R1/R2) rides entirely on ``killtest.tokens.count_tokens`` — a
regex-BPE *proxy* (alnum runs -> max(1,(len+3)//4) tokens; each punctuation
char -> 1 token). Before that proxy is load-bearing we must answer:

  Q1 (absolute bias): how far is the proxy from a real model tokenizer?
  Q2 (DIFFERENTIAL bias, the load-bearing one): does the proxy count
     code-bodies (the text arm's cost) differently from law/signature text
     (the Tao arm's cost)? A *uniform* bias cancels in the ratio ρ and in the
     M1_tao/M1_text comparison; only a bias that favours one genre over the
     other can move the verdict.
  Q3 (robustness): does the R1/R2 outcome survive across a spread of plausible
     tokenizer models? If Tao's advantage holds under every model, the proxy
     risk is bounded regardless of which exact tokenizer a real run would use.

Q1 needs a real tokenizer (tiktoken/anthropic); included as a column *iff*
importable, else recorded as a deferred cross-check. Q2/Q3 are fully offline
and are the ones that actually gate the verdict's credibility.

Run:  PYTHONPATH=holon-bench/runners python3 -m killtest.calibrate_tokens
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import math
import pathlib
import re

from killtest.tokens import count_tokens
from killtest.config import resolve_paths


def _workspace() -> pathlib.Path:
    return resolve_paths().workspace

# --------------------------------------------------------------- tokenizer models
# Each maps text -> token count. They bracket the plausible space: from "no
# sub-word merging" (ws_punct, an upper bound) through the proxy and char-rate
# models to a "code-fragmenting" BPE analogue that splits identifiers (real BPE
# fragments snake/camel identifiers harder than the proxy's flat len/4).

_WORD = re.compile(r"[A-Za-z0-9_]+|[^\sA-Za-z0-9_]")
_IDENT_SPLIT = re.compile(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])|_")


def tok_ws_punct(text: str) -> int:
    """Every word and every punctuation char = 1 token. No merging => upper bound."""
    return len(_WORD.findall(text))


def tok_chars(divisor: float):
    def f(text: str) -> int:
        return max(1, math.ceil(len(text) / divisor))
    return f


def tok_code_split(text: str) -> int:
    """BPE analogue that fragments identifiers: split each alnum run on
    snake_case / camelCase, then charge ceil(subword/4); each punct = 1 token.
    Models a real tokenizer fragmenting `sorted_unique_insert` into several
    pieces rather than the proxy's single len/4 estimate."""
    n = 0
    for m in _WORD.findall(text):
        if re.fullmatch(r"[A-Za-z0-9_]+", m):
            parts = _IDENT_SPLIT.findall(m) or [m]
            n += sum(max(1, math.ceil(len(p) / 4)) for p in parts if p != "_")
            n += m.count("_")  # underscores survive as joiners in many vocabs
        else:
            n += 1
    return n


TOKENIZERS: dict[str, callable] = {
    "proxy": count_tokens,        # the instrument under test
    "chars/4.0": tok_chars(4.0),
    "chars/3.5": tok_chars(3.5),  # ~English BPE rate
    "ws_punct": tok_ws_punct,     # no-merge upper bound
    "code_split": tok_code_split, # identifier-fragmenting BPE analogue
}

# Optional real tokenizer (Q1). Absent in this env -> recorded as deferred.
try:  # pragma: no cover - environment dependent
    import tiktoken  # type: ignore

    _enc = tiktoken.get_encoding("o200k_base")
    TOKENIZERS["tiktoken_o200k"] = lambda t: len(_enc.encode(t))
    REAL_TOKENIZER = "tiktoken_o200k"
except Exception:
    REAL_TOKENIZER = None


# ---------------------------------------------------------------------- corpus
def load_corpus() -> dict[str, dict[str, str]]:
    """Return {'bodies': {op: src}, 'laws': {op: law}, 'sigs': {op: sig}} from the
    committed indicative library if reachable, else a small embedded sample. The
    indicative library is the current best proxy for the Stage-1 A2 corpus; the
    real A2 corpus is re-run through this tool at A6."""
    demo = _workspace() / "runs" / "tao-killtest-indicative" / "tao_token_demo2.py"
    if demo.is_file():
        spec = importlib.util.spec_from_file_location("_killtest_indicative", demo)
        mod = importlib.util.module_from_spec(spec)
        with contextlib.redirect_stdout(io.StringIO()):  # the demo prints on import
            spec.loader.exec_module(mod)  # type: ignore
        return {"bodies": mod.BODIES, "laws": mod.LAWS, "sigs": mod.SIGS}
    # Embedded fallback (representative; not the full library).
    return {
        "bodies": {
            "agg_sum_bounded": ("pub fn agg_sum_bounded(xs: &[i64], cap: i64) -> i64 {\n"
                                "    let mut acc: i64 = 0;\n"
                                "    for &x in xs { acc = acc.saturating_add(x); if acc > cap { acc = cap; } }\n"
                                "    acc\n}"),
        },
        "laws": {"agg_sum_bounded": "laws: identity 0; associative; monotone; result=min(sum,cap); result<=cap."},
        "sigs": {"agg_sum_bounded": "fn agg_sum_bounded(xs: &[i64], cap: i64) -> i64"},
    }


def _sum(tok, texts) -> int:
    return sum(tok(t) for t in texts)


def calibrate() -> dict:
    corpus = load_corpus()
    bodies, laws, sigs = corpus["bodies"], corpus["laws"], corpus["sigs"]
    ops = list(bodies)

    rows = {}
    for name, tok in TOKENIZERS.items():
        body_chars = sum(len(bodies[o]) for o in ops)
        law_chars = sum(len(laws[o]) for o in ops if o in laws)
        sb = _sum(tok, [bodies[o] for o in ops])
        sl = _sum(tok, [laws[o] for o in ops if o in laws])
        ss = _sum(tok, [sigs[o] for o in ops if o in sigs])
        rows[name] = {
            "body_tok": sb, "law_tok": sl, "sig_tok": ss,
            "body_tok_per_char": round(sb / body_chars, 4),
            "law_tok_per_char": round(sl / law_chars, 4),
            # Q2 differential-bias signal: code rate / law rate. If this is ~equal
            # across tokenizers, the proxy is not differentially biased.
            "code_vs_law_rate": round((sb / body_chars) / (sl / law_chars), 4),
            # Q3: the Tao-economy ratio the verdict cares about.
            "rho_law_over_body": round(sl / sb, 4),
            "sig_plus_law_over_body": round((ss + sl) / sb, 4),
        }
    return {"ops": ops, "n_ops": len(ops), "real_tokenizer": REAL_TOKENIZER, "rows": rows}


def standing_accounting_note(per_cycle_standing: int, body_dep: int, k_edits: int) -> dict:
    """v1 §3 counts standing every cycle. Show how much a session-amortized view
    (standing paid once, deps per edit) would move per-edit M1 over k edits."""
    per_cycle = per_cycle_standing + body_dep
    amortized = body_dep + per_cycle_standing / k_edits
    return {
        "k_edits": k_edits,
        "per_cycle_M1": per_cycle,
        "amortized_M1": round(amortized, 1),
        "ratio_amortized_over_percycle": round(amortized / per_cycle, 4),
        "note": ("v1 §3 keeps per-cycle standing for BOTH arms, so standing cancels "
                 "in the cross-arm comparison; amortization changes absolute M1 but "
                 "not the arm ordering. Recorded for transparency, not a rule change."),
    }


def main() -> None:
    cal = calibrate()
    proxy = cal["rows"]["proxy"]
    rhos = [r["rho_law_over_body"] for r in cal["rows"].values()]
    rates = [r["code_vs_law_rate"] for r in cal["rows"].values()]

    print(f"== count_tokens calibration ==  n_ops={cal['n_ops']}  "
          f"real_tokenizer={cal['real_tokenizer'] or 'DEFERRED (not installed)'}\n")
    hdr = f"{'tokenizer':<16}{'body':>7}{'law':>6}{'sig':>6}{'b/char':>8}{'l/char':>8}{'code/law':>9}{'rho':>7}{'(s+l)/b':>9}"
    print(hdr)
    for name, r in cal["rows"].items():
        print(f"{name:<16}{r['body_tok']:>7}{r['law_tok']:>6}{r['sig_tok']:>6}"
              f"{r['body_tok_per_char']:>8}{r['law_tok_per_char']:>8}"
              f"{r['code_vs_law_rate']:>9}{r['rho_law_over_body']:>7}{r['sig_plus_law_over_body']:>9}")

    print(f"\nQ2 differential bias  code/law rate: min {min(rates):.3f}  max {max(rates):.3f}  "
          f"spread {max(rates)-min(rates):.3f}")
    print(f"Q3 robustness         rho spread: min {min(rhos):.3f}  max {max(rhos):.3f}  "
          f"(proxy rho={proxy['rho_law_over_body']})")
    print(f"   verdict-robust? Tao law/body advantage (rho<1) holds under ALL models: "
          f"{all(x < 1 for x in rhos)}")

    note = standing_accounting_note(per_cycle_standing=742, body_dep=1430, k_edits=10)
    print(f"\nstanding accounting (illustrative k={note['k_edits']}): per-cycle M1={note['per_cycle_M1']} "
          f"vs amortized M1={note['amortized_M1']} "
          f"({note['ratio_amortized_over_percycle']}x) — cancels cross-arm.")

    out = {"calibration": cal, "standing": note,
           "q2_code_vs_law_rate_spread": round(max(rates) - min(rates), 4),
           "q3_rho_spread": [min(rhos), max(rhos)],
           "q3_advantage_robust": all(x < 1 for x in rhos)}
    dest = _workspace() / "runs" / "tao-killtest-calibration"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "calibration.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {dest/'calibration.json'}")


if __name__ == "__main__":
    main()
