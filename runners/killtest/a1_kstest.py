#!/usr/bin/env python3
"""A1 adequacy gate: KS-test the library's per-op body-size distribution against a
version-pinned real codebase D (v1 §1 A1). Must FAIL TO REJECT at alpha=0.05, i.e.
p > 0.05 — that is what stops bodies being engineered pro/anti-Tao.

Two pieces, both offline (scipy absent -> two-sample KS implemented here):
  * a Rust `fn` body extractor that counts body tokens with the SAME tokenizer the
    verdict uses (killtest.tokens.count_tokens). A small lexer blanks comment and
    string/char-literal interiors (and does NOT trip on lifetimes) so braces inside
    them never corrupt body brace-matching.
  * a two-sample Kolmogorov-Smirnov test (Numerical-Recipes `kstwo` asymptotic p).

CLI:
  measure <dir> [--out f.json] [--min-tokens N]   # dump D's (or a lib's) body dist
  kstest  <a.json> <b.json>                        # two-sample KS + verdict
  selftest                                          # KS impl sanity (D vs D -> p~1)
"""
from __future__ import annotations

import json
import math
import pathlib
import re
import sys

from killtest.tokens import count_tokens

_FN = re.compile(r"\bfn\s+([A-Za-z_]\w*)")


def _blank_noncode(src: str) -> str:
    """Return src with comment + string/char literal *interiors* replaced by spaces
    (delimiters kept, length preserved) so brace-matching sees only code braces.
    Handles //, /* */ (nested), "..", r#".."#, '..' char vs 'a lifetime, b"..", '\\n'."""
    out = list(src)
    i, n = 0, len(src)

    def blank(a: int, b: int) -> None:
        for k in range(a, b):
            if out[k] != "\n":
                out[k] = " "

    while i < n:
        c = src[i]
        if c == "/" and i + 1 < n and src[i + 1] == "/":
            j = src.find("\n", i)
            j = n if j < 0 else j
            blank(i + 2, j)
            i = j
        elif c == "/" and i + 1 < n and src[i + 1] == "*":
            depth, j = 1, i + 2
            while j < n and depth:
                if src[j] == "/" and j + 1 < n and src[j + 1] == "*":
                    depth += 1; j += 2
                elif src[j] == "*" and j + 1 < n and src[j + 1] == "/":
                    depth -= 1; j += 2
                else:
                    j += 1
            blank(i + 2, j - 2)
            i = j
        elif c == "r" and i + 1 < n and src[i + 1] in '"#':
            # raw string r#*"..."#*
            k = i + 1; hashes = 0
            while k < n and src[k] == "#":
                hashes += 1; k += 1
            if k < n and src[k] == '"':
                close = '"' + "#" * hashes
                j = src.find(close, k + 1)
                j = n if j < 0 else j + len(close)
                blank(k + 1, j - len(close))
                i = j
            else:
                i += 1
        elif c == '"':
            j = i + 1
            while j < n:
                if src[j] == "\\":
                    j += 2; continue
                if src[j] == '"':
                    break
                j += 1
            blank(i + 1, j)
            i = j + 1
        elif c == "'":
            # char literal 'x' / '\n' / '\u{..}'  vs  lifetime 'a  vs  label 'l:
            m = re.match(r"'(\\.|\\u\{[0-9A-Fa-f]+\}|[^'\\])'", src[i:])
            if m:
                blank(i + 1, i + m.end() - 1)
                i += m.end()
            else:
                i += 1  # lifetime / label tick — leave as-is
        else:
            i += 1
    return "".join(out)


def extract_fn_bodies(src: str) -> list[tuple[str, int]]:
    """(name, token-count) of every `fn` body in src (skeleton-matched, real tokens)."""
    skel = _blank_noncode(src)
    sizes: list[tuple[str, int]] = []
    for m in _FN.finditer(skel):
        fn_name = m.group(1)
        # find the body-opening brace; bail if a ';' first (sig-only / trait decl).
        k = m.end()
        depth_angle = 0
        open_brace = -1
        while k < len(skel):
            ch = skel[k]
            if ch == "<":
                depth_angle += 1
            elif ch == ">" and depth_angle:
                depth_angle -= 1
            elif ch == ";" and depth_angle == 0:
                break
            elif ch == "{" and depth_angle == 0:
                open_brace = k
                break
            k += 1
        if open_brace < 0:
            continue
        depth, j = 1, open_brace + 1
        while j < len(skel) and depth:
            if skel[j] == "{":
                depth += 1
            elif skel[j] == "}":
                depth -= 1
            j += 1
        body = src[open_brace + 1: j - 1]
        tok = count_tokens(body)
        if tok > 0:
            sizes.append((fn_name, tok))
    return sizes


def measure_dir(root: pathlib.Path, min_tokens: int = 1, exclude: set[str] | None = None) -> dict:
    exclude = exclude or set()
    named: list[tuple[str, int]] = []
    files = 0
    for p in sorted(root.rglob("*.rs")):
        if "/tests/" in p.as_posix() or p.name.endswith("_test.rs"):
            continue
        files += 1
        for name, s in extract_fn_bodies(p.read_text(errors="replace")):
            if s >= min_tokens and name not in exclude:
                named.append((name, s))
    named.sort(key=lambda t: t[1])
    sizes = [s for _, s in named]
    return {"root": str(root), "files": files, "n": len(sizes),
            "min": sizes[0] if sizes else 0, "median": _median(sizes),
            "p90": _pct(sizes, 90), "max": sizes[-1] if sizes else 0,
            "mean": round(sum(sizes) / len(sizes), 1) if sizes else 0,
            "sizes": sizes, "named": named}


def _median(v: list[int]) -> float:
    if not v:
        return 0.0
    s = sorted(v); m = len(s) // 2
    return float(s[m]) if len(s) % 2 else (s[m - 1] + s[m]) / 2


def _pct(v: list[int], p: float) -> float:
    if not v:
        return 0.0
    s = sorted(v)
    return float(s[min(len(s) - 1, math.ceil(p / 100 * len(s)) - 1)])


def _ks_pvalue(d: float, ne: float) -> float:
    """Kolmogorov Q-function p-value (Numerical Recipes `probks`)."""
    lam = (math.sqrt(ne) + 0.12 + 0.11 / math.sqrt(ne)) * d
    a2 = -2.0 * lam * lam
    s, fac, prev = 0.0, 2.0, 0.0
    for k in range(1, 101):
        term = fac * math.exp(a2 * k * k)
        s += term
        if abs(term) <= 1e-3 * prev or abs(term) <= 1e-8 * s:
            return max(0.0, min(1.0, s))
        fac = -fac
        prev = abs(term)
    return 1.0


def ks_two_sample(x: list[int], y: list[int]) -> dict:
    xs, ys = sorted(x), sorted(y)
    nx, ny = len(xs), len(ys)
    vals = sorted(set(xs) | set(ys))

    def cdf(s, v):
        # fraction <= v
        import bisect
        return bisect.bisect_right(s, v) / len(s)

    dstat = max(abs(cdf(xs, v) - cdf(ys, v)) for v in vals)
    ne = nx * ny / (nx + ny)
    p = _ks_pvalue(dstat, ne)
    return {"D": round(dstat, 4), "p_value": round(p, 4), "nx": nx, "ny": ny,
            "alpha": 0.05, "fail_to_reject": p > 0.05,
            "verdict": "A1 PASS (indistinguishable)" if p > 0.05 else "A1 FAIL (reject: distributions differ)"}


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__); return 2
    cmd = argv[0]
    if cmd == "measure":
        root = pathlib.Path(argv[1]).expanduser()
        mt = 1
        out = None
        excl: set[str] = set()
        for i, a in enumerate(argv):
            if a == "--min-tokens":
                mt = int(argv[i + 1])
            if a == "--out":
                out = pathlib.Path(argv[i + 1])
            if a == "--exclude":
                excl = set(argv[i + 1].split(","))
        dist = measure_dir(root, mt, excl)
        summary = {k: v for k, v in dist.items() if k != "sizes"}
        print(json.dumps(summary, indent=2))
        if out:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(dist, indent=2), encoding="utf-8")
            print(f"wrote {out} ({dist['n']} fn bodies)")
        return 0
    if cmd == "kstest":
        a = json.loads(pathlib.Path(argv[1]).read_text())["sizes"]
        b = json.loads(pathlib.Path(argv[2]).read_text())["sizes"]
        print(json.dumps(ks_two_sample(a, b), indent=2))
        return 0
    if cmd == "selftest":
        import random
        rng = random.Random(0)
        d = [rng.randint(5, 300) for _ in range(400)]
        same = ks_two_sample(d, d[: len(d) // 2])
        diff = ks_two_sample(d, [v * 3 + 50 for v in d])
        ok = same["fail_to_reject"] and not diff["fail_to_reject"]
        print(f"selftest: same->p={same['p_value']} (expect>0.05), "
              f"shifted->p={diff['p_value']} (expect<0.05) :: {'PASS' if ok else 'FAIL'}")
        return 0 if ok else 1
    print(f"unknown command: {cmd}"); return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
