"""Suite management: hash commitment (G3), acceptance install, hidden isolation.

Three hard rules from the prereg + task brief:

* The acceptance rendition is the *only* suite copied into an arm-visible mount
  (prereg A.3 — visible to both arms after G3).
* The hidden/mutation suite is read ONLY at scoring time, ONLY from outside every
  arm mount, and its path / case-ids / contents must NEVER appear in any
  arm-visible file, prompt, or log. A leak voids M10 ⇒ INCONCLUSIVE
  (spike plan §3, task req 3).
* All suite hashes (abstract + each rendition) are committed to the run log
  before run 1 — the G3 witness (prereg §5, spike plan P2).
"""

from __future__ import annotations

import pathlib
import shutil
from dataclasses import dataclass
from typing import Any

from . import config


# arm -> rendition subdir name inside the private suite tree.
ARM_RENDITION = {"tao": "tao", "baseline": "rust"}


def compute_suite_hashes(paths: config.Paths) -> dict[str, Any]:
    """Hash every suite artifact for the G3 commitment.

    Hashes file *content* (digest only) — safe over the hidden suite: the digest
    is committed, the contents are not disclosed. Includes a per-tree roll-up so
    a single value witnesses the whole hidden suite."""
    acc = paths.acceptance_dir
    hid = paths.hidden_dir
    out: dict[str, Any] = {"algo": config.HASH_ALGO, "acceptance": {}, "hidden": {}}

    if (acc / "abstract.json").exists():
        out["acceptance"]["abstract"] = config.hash_file(acc / "abstract.json")
    for arm, sub in ARM_RENDITION.items():
        d = acc / sub
        if d.exists():
            out["acceptance"][f"rendition_{arm}"] = config.hash_tree(d)

    if (hid / "abstract.json").exists():
        out["hidden"]["abstract"] = config.hash_file(hid / "abstract.json")
    for arm, sub in ARM_RENDITION.items():
        d = hid / sub
        if d.exists():
            out["hidden"][f"rendition_{arm}"] = config.hash_tree(d)
    if hid.exists():
        out["hidden"]["tree_rollup"] = config.hash_tree(hid)
    return out


def install_acceptance_assets(paths: config.Paths, arm: str, mount: pathlib.Path) -> list[str]:
    """Copy the acceptance rendition for ``arm`` into the arm-visible mount.

    Returns the list of installed relative paths. Only the acceptance rendition is
    ever installed — the hidden suite is never touched here."""
    sub = ARM_RENDITION[arm]
    src = paths.acceptance_dir / sub
    if not src.exists():
        raise SystemExit(f"acceptance rendition missing for arm {arm}: {src}")
    dst = mount / "acceptance"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    # the shared abstract is acceptance-only and visible (semantics doc).
    abstract = paths.acceptance_dir / "abstract.json"
    if abstract.exists():
        shutil.copy2(abstract, mount / "acceptance" / "abstract.json")
    return sorted(p.relative_to(mount).as_posix()
                  for p in dst.rglob("*") if p.is_file())


@dataclass
class LeakReport:
    clean: bool
    hits: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {"clean": self.clean, "hits": self.hits}


def hidden_fingerprints(paths: config.Paths) -> list[str]:
    """Strings whose appearance in any arm-visible surface is a hidden-suite leak:
    the hidden directory path and every hidden case id (H01..). Contents are NOT
    used as fingerprints — we never load hidden bodies into the leak scanner's
    own surface beyond the case-id tokens, which are the minimal witness."""
    # The full hidden path is a meaningful leak signal; the bare word "hidden"
    # is NOT (the task brief legitimately says "a held-out hidden suite"), so we
    # fingerprint the path + each hidden case id, never the generic token.
    fps: list[str] = [str(paths.hidden_dir)]
    import json
    abstract = paths.hidden_dir / "abstract.json"
    if abstract.exists():
        data = json.loads(abstract.read_text(encoding="utf-8"))
        for case in data.get("cases", []):
            cid = case.get("id")
            if cid:
                fps.append(str(cid))
    # de-dup, keep stable order.
    seen: set[str] = set()
    ordered = []
    for f in fps:
        if f and f not in seen:
            seen.add(f)
            ordered.append(f)
    return ordered


def scan_for_leak(roots: list[pathlib.Path], fingerprints: list[str]) -> LeakReport:
    """Scan arm-visible roots (mounts + logs) for any hidden fingerprint."""
    hits: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file()]
        for path in files:
            try:
                raw = path.read_bytes()
            except OSError:
                continue
            # P5 shakedown finding: compiled artifacts read as lossy text
            # false-positive on short case-id fingerprints (e.g. "H04" occurs
            # in random bytes). Binaries cannot leak prompt-visible text to an
            # agent; skip them, and require word-boundary matches for short
            # ids so e.g. "H041abc" in a hash does not trip the scan.
            if b"\x00" in raw[:4096]:
                continue
            text = raw.decode("utf-8", errors="ignore")
            for fp in fingerprints:
                if not fp:
                    continue
                if len(fp) < 8:
                    import re
                    if re.search(rf"\b{re.escape(fp)}\b", text):
                        hits.append(f"{path}:{fp}")
                elif fp in text:
                    hits.append(f"{path}:{fp}")
    return LeakReport(clean=not hits, hits=sorted(hits))


def assert_hidden_outside_mounts(paths: config.Paths, arm_mounts: list[pathlib.Path]) -> None:
    """Structural guarantee: the hidden suite dir is not inside any arm mount."""
    hid = paths.hidden_dir.resolve()
    for mount in arm_mounts:
        m = mount.resolve()
        if hid == m or m in hid.parents or hid in m.parents:
            raise SystemExit(
                f"hidden suite {hid} overlaps arm mount {m}: M10 would be void")
