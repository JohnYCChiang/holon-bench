"""Per-edit-cycle token accounting (prereg M1/M2).

M1/M2 count "tokens placed in the agent's context window attributable to the
edit cycle (bundle or file/repo-map content + diagnostics)" (prereg §3), with
mechanics-doc / prompt overhead counted in (prereg §5 — "the Tao arm does not
get its instruction manual for free").

Two design decisions, both made for *fairness* between arms:

1. A single deterministic tokenizer is applied to the literal text each arm
   places in context. Using one counter for both arms is what makes R1/R2
   comparable. ``tao-port ctx`` also reports its own bundle token count; that is
   logged as an *observational* field (M7/M8 colour), never as the M1/M2 number.
2. Standing context (task brief + the arm's mechanics doc) occupies the window
   on *every* edit cycle, so its token cost is added to every cycle. This is the
   honest reading of "tokens placed in the context window attributable to the
   edit cycle": the manual is really there each cycle. Equal treatment both arms.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


TOKENIZER_NAME = "holon-bench/regex-bpe-proxy-v1"

# Word/number/operator-ish runs + standalone punctuation. A deterministic,
# dependency-free proxy for GPT-style subword counts: long alphanumeric runs are
# split on the ~4-char boundary BPE tends to land near, punctuation counts singly.
_WORD = re.compile(r"[A-Za-z0-9_]+|[^\sA-Za-z0-9_]")


def count_tokens(text: str) -> int:
    if not text:
        return 0
    total = 0
    for tok in _WORD.findall(text):
        if tok.isalnum() or "_" in tok:
            # subword split: ~4 chars/token, at least one.
            total += max(1, (len(tok) + 3) // 4)
        else:
            total += 1
    return total


# edit-cycle entry categories (prereg §3 surfaces).
CAT_STANDING = "standing"      # task brief + mechanics doc, present every cycle
CAT_CONTEXT = "context"        # tao bundle OR baseline file/repo-map content
CAT_DIAGNOSTIC = "diagnostic"  # structured diagnostics / test-failure output


@dataclass
class LedgerEntry:
    category: str
    label: str
    tokens: int
    observational: dict[str, Any] = field(default_factory=dict)


@dataclass
class EditCycle:
    """One submit→diagnostics window. ``accepted`` marks an edit that the harness
    accepted and that survives to the final solution (prereg §3 "accepted edit");
    only accepted cycles feed M1/M2."""

    index: int
    kind: str               # "txn" | "file_write"
    accepted: bool = False
    survived: bool = True    # set False if later fully reverted
    entries: list[LedgerEntry] = field(default_factory=list)

    def add(self, category: str, label: str, text: str = "", *,
            tokens: int | None = None, observational: dict[str, Any] | None = None) -> int:
        n = tokens if tokens is not None else count_tokens(text)
        self.entries.append(LedgerEntry(category, label, n, observational or {}))
        return n

    def total(self) -> int:
        return sum(e.tokens for e in self.entries)

    def breakdown(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for e in self.entries:
            out[e.category] = out.get(e.category, 0) + e.tokens
        return out

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "kind": self.kind,
            "accepted": self.accepted,
            "survived": self.survived,
            "tokens_total": self.total(),
            "tokens_by_category": self.breakdown(),
            "entries": [
                {"category": e.category, "label": e.label, "tokens": e.tokens,
                 **({"observational": e.observational} if e.observational else {})}
                for e in self.entries
            ],
        }


@dataclass
class TokenLedger:
    """The per-run token ledger. Standing-context tokens are injected into every
    cycle at open() time so M1/M2 reflect the full window."""

    standing_tokens: int = 0
    standing_label: str = "standing-context"
    cycles: list[EditCycle] = field(default_factory=list)

    def set_standing(self, *docs: str, label: str = "standing-context") -> int:
        self.standing_tokens = sum(count_tokens(d) for d in docs)
        self.standing_label = label
        return self.standing_tokens

    def open_cycle(self, kind: str) -> EditCycle:
        c = EditCycle(index=len(self.cycles), kind=kind)
        if self.standing_tokens:
            c.add(CAT_STANDING, self.standing_label, tokens=self.standing_tokens)
        self.cycles.append(c)
        return c

    def accepted_surviving(self) -> list[EditCycle]:
        return [c for c in self.cycles if c.accepted and c.survived]

    def per_accepted_edit_tokens(self) -> list[int]:
        return [c.total() for c in self.accepted_surviving()]

    def to_dict(self) -> dict[str, Any]:
        return {
            "tokenizer": TOKENIZER_NAME,
            "standing_tokens": self.standing_tokens,
            "cycle_count": len(self.cycles),
            "accepted_edit_count": len(self.accepted_surviving()),
            "cycles": [c.to_dict() for c in self.cycles],
        }


def median(values: list[float]) -> float | None:
    if not values:
        return None
    s = sorted(values)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2.0


def percentile(values: list[float], pct: float) -> float | None:
    """Linear-interpolation percentile (pct in [0,100]); matches numpy default."""
    if not values:
        return None
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    rank = (pct / 100.0) * (len(s) - 1)
    lo = int(rank)
    hi = min(lo + 1, len(s) - 1)
    frac = rank - lo
    return s[lo] + (s[hi] - s[lo]) * frac
