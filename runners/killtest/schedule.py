"""Run scheduling (interleave arms) + arm-blind M5 review packaging.

prereg §5 commitments realised here:
* the same reviewer reviews both arms, interleaved;
* review order is randomized per run pair (seeded for reproducibility);
* the reviewer sees an arm-blind package "where the artifact allows" — the blind
  label -> (run_id, arm) mapping is written to a SEALED file kept out of the
  reviewer's directory, so review minutes (M5) are not biased by arm identity.
"""

from __future__ import annotations

import json
import pathlib
import random
from dataclasses import dataclass, field
from typing import Any

from . import config


@dataclass
class ScheduledRun:
    pair_index: int
    arm: str
    run_index: int
    review_order: int   # 0 or 1 within the pair (randomized)

    @property
    def run_id(self) -> str:
        return f"run-{self.run_index:02d}-{self.arm}"

    def to_dict(self) -> dict[str, Any]:
        return {"pair_index": self.pair_index, "arm": self.arm,
                "run_index": self.run_index, "run_id": self.run_id,
                "review_order": self.review_order}


def build_schedule(n_per_arm: int = config.N_PER_ARM, *, seed: int = 0) -> list[ScheduledRun]:
    """Interleave: pair i runs both arms; execution alternates arm-first by parity;
    review order within each pair is randomized by the seeded RNG."""
    rng = random.Random(seed)
    plan: list[ScheduledRun] = []
    for i in range(n_per_arm):
        arms = list(config.ARMS)
        if i % 2 == 1:
            arms = arms[::-1]                 # alternate execution order across pairs
        review_first = rng.randint(0, 1)      # randomize review order per pair
        for arm in arms:
            order = 0 if (arm == config.ARMS[review_first]) else 1
            plan.append(ScheduledRun(pair_index=i, arm=arm, run_index=i, review_order=order))
    return plan


# ------------------------------------------------------------------ M5 packaging

@dataclass
class ReviewPackage:
    blind_id: str
    run_id: str
    arm: str
    package_dir: pathlib.Path

    def to_dict(self) -> dict[str, Any]:
        return {"blind_id": self.blind_id, "run_id": self.run_id, "arm": self.arm,
                "package_dir": str(self.package_dir)}


def package_for_review(run_dir: pathlib.Path, *, run_id: str, arm: str,
                       artifact_paths: list[pathlib.Path], review_root: pathlib.Path,
                       seed: int = 0) -> ReviewPackage:
    """Copy a run's final artifact into an arm-blind package; seal the mapping.

    The blind id is derived from a seeded hash of the run_id so the reviewer
    cannot infer the arm from the directory name. The sealed map lives in
    ``review_root/.sealed/`` — read only after M5 minutes are recorded."""
    import hashlib
    blind = hashlib.sha256(f"{seed}:{run_id}".encode()).hexdigest()[:12]
    pkg = review_root / f"pkg-{blind}"
    pkg.mkdir(parents=True, exist_ok=True)
    for src in artifact_paths:
        if src.exists():
            dst = pkg / src.name
            dst.write_bytes(src.read_bytes())

    sealed_dir = review_root / ".sealed"
    sealed_dir.mkdir(parents=True, exist_ok=True)
    (sealed_dir / f"{blind}.json").write_text(
        json.dumps({"blind_id": blind, "run_id": run_id, "arm": arm}, indent=2),
        encoding="utf-8")
    return ReviewPackage(blind_id=blind, run_id=run_id, arm=arm, package_dir=pkg)


@dataclass
class ReviewRecord:
    blind_id: str
    minutes: float
    reviewer: str = config.M5_REVIEWER
    defects: list[dict[str, Any]] = field(default_factory=list)

    def resolve_arm(self, review_root: pathlib.Path) -> dict[str, Any]:
        sealed = review_root / ".sealed" / f"{self.blind_id}.json"
        data = json.loads(sealed.read_text(encoding="utf-8"))
        return {"run_id": data["run_id"], "arm": data["arm"],
                "minutes": self.minutes, "reviewer": self.reviewer,
                "defects": self.defects}
