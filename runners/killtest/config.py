"""Frozen experiment constants + path layout for the Tao Stage 0 kill test.

Every numeric threshold and metric definition below is a faithful transcription
of ``tao/docs/tao-killtest-prereg-v0.md`` (RATIFIED AND FROZEN 2026-06-10) with a
``prereg_ref`` pointing at the governing section. The harness implements this
document; it does not reinterpret it. Drift is caught by recording PREREG_SHA256
into the run log — if the frozen file changes, the recorded hash changes and the
experiment is INCONCLUSIVE per prereg §4 (re-register v1).
"""

from __future__ import annotations

import hashlib
import os
import pathlib
from dataclasses import dataclass, field
from typing import Any


# --------------------------------------------------------------------------- paths

def bench_root(start: str | os.PathLike[str] | None = None) -> pathlib.Path:
    """Locate the holon-bench root (dir containing manifest/benchmark.yaml)."""
    root = pathlib.Path(start or __file__).resolve()
    if root.is_file():
        root = root.parent
    while root != root.parent:
        if (root / "manifest" / "benchmark.yaml").exists():
            return root
        root = root.parent
    raise SystemExit("could not locate holon-bench root (manifest/benchmark.yaml)")


@dataclass(frozen=True)
class Paths:
    """Resolved filesystem layout. Arm mounts live under run_root; the private
    suite (acceptance + hidden) lives outside every arm mount by construction."""

    bench: pathlib.Path
    workspace: pathlib.Path
    tao_repo: pathlib.Path
    tao_port: pathlib.Path
    registry: pathlib.Path
    prereg: pathlib.Path
    spike_plan: pathlib.Path
    private_suite: pathlib.Path
    run_root: pathlib.Path

    @property
    def acceptance_dir(self) -> pathlib.Path:
        return self.private_suite / "acceptance"

    @property
    def hidden_dir(self) -> pathlib.Path:
        """Read ONLY at scoring time, ONLY from outside every arm mount.
        Never copy this path's contents into an arm-visible file/prompt/log."""
        return self.private_suite / "hidden"


def resolve_paths(
    bench: pathlib.Path | None = None,
    run_root: str | os.PathLike[str] | None = None,
    private_suite: str | os.PathLike[str] | None = None,
    pack: "TaskPack | None" = None,
) -> Paths:
    b = bench_root(bench)
    workspace = b.parent
    tao_repo = workspace / "tao"
    home = pathlib.Path(os.path.expanduser("~"))
    # A task pack selects its own prereg file + private-suite subdir; with no pack
    # the layout is byte-identical to the frozen v0 default.
    prereg_name = pack.prereg_filename if pack else "tao-killtest-prereg-v0.md"
    priv_base = pathlib.Path(private_suite) if private_suite else home / "tao-killtest-private"
    priv = priv_base / pack.private_subdir if (pack and pack.private_subdir) else priv_base
    runs = pathlib.Path(run_root) if run_root else workspace / "runs" / "tao-killtest"
    return Paths(
        bench=b,
        workspace=workspace,
        tao_repo=tao_repo,
        tao_port=tao_repo / "target" / "debug" / "tao-port",
        registry=tao_repo / "artifacts" / "trusted-toolchain-registry-v0.json",
        prereg=tao_repo / "docs" / prereg_name,
        spike_plan=tao_repo / ".claude" / "tasks" / "tao-stage0-spike-plan.md",
        private_suite=priv.resolve(),
        run_root=runs,
    )


# --------------------------------------------------------- frozen experiment values

# prereg §2 / Appendix A.5 / §7 — pinned at ratification, immutable.
MODEL_ID_PINNED = "claude-fable-5"      # exact model ID recorded in run log at first run (§7)
N_PER_ARM = 5                           # Appendix A.5; §7 ratified
M5_REVIEWER = "John"                    # §7 ratified
CAP = 64                                # Appendix A.1
ARMS = ("tao", "baseline")
OPERATIONS = ("empty", "insert", "member", "size")  # Appendix A.1
LAWS = ("L-ord", "L-mem", "L-idem", "L-comm", "L-size")  # Appendix A.1

# prereg §4 decision-rule thresholds (ratified, never touched).
R1_MEDIAN_FACTOR = 0.7   # median(M1_T) <= 0.7 * median(M1_B)
R2_P90_FACTOR = 0.8      # p90(M2_T)    <= 0.8 * p90(M2_B)
NO_HARM_ALLOWANCE = 0.10  # R3-R5: Tao median may exceed baseline by at most 10%

PREREG_VERSION = "tao-killtest-prereg-v0"


@dataclass(frozen=True)
class Metric:
    id: str
    name: str
    prereg_ref: str
    decision: bool        # does it feed the §4 decision rule?


# prereg §3 metric table — the list is frozen; observational metrics may be added
# to the LOG but cannot affect the verdict (prereg §5).
METRICS: tuple[Metric, ...] = (
    Metric("M1", "median context tokens per accepted edit", "prereg §3", True),
    Metric("M2", "p90 context tokens per accepted edit", "prereg §3", True),
    Metric("M3", "edits-to-green", "prereg §3", True),
    Metric("M4", "verifier round-trips", "prereg §3", False),
    Metric("M5", "human review minutes", "prereg §3", True),
    Metric("M6", "signature thinness bytes (Tao only)", "prereg §3", False),
    Metric("M7", "% context bundle: signatures vs bodies (Tao only)", "prereg §3", False),
    Metric("M8", "body fetch count (Tao only)", "prereg §3", False),
    Metric("M9", "failed edit recovery count", "prereg §3", False),
    Metric("M10", "mutation / hidden tests pass rate", "prereg §3", True),
    Metric("M11", "wrong-code severity", "prereg §3", True),
)

# prereg A.1 placeholders that arm templates carry; substituted from the run's
# world manifest (prim:*) plus the agent's submitted def ids (the rest).
TEMPLATE_PLACEHOLDERS = ("{EMPTY}", "{INSERT}", "{MEMBER}", "{SIZE}", "{EID}", "{prim:NAME}")


# ---------------------------------------------------------------- content hashing

HASH_ALGO = "sha256"


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_file(path: pathlib.Path) -> str:
    return hash_bytes(path.read_bytes())


def hash_tree(root: pathlib.Path) -> str:
    """Stable hash over a directory: sorted ``relpath\\0sha256`` lines.

    Hashes file *content*, never reveals it — safe to compute over the hidden
    suite (the digest is committed; the contents are not)."""
    lines: list[str] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        lines.append(f"{rel}\0{hash_file(path)}")
    return hash_bytes("\n".join(lines).encode("utf-8"))


def prereg_hash(paths: Paths) -> str:
    return hash_file(paths.prereg) if paths.prereg.exists() else "MISSING"


def registry_hash(paths: Paths) -> str:
    return hash_file(paths.registry) if paths.registry.exists() else "MISSING"


def harness_version_hash(paths: Paths) -> str:
    """Content hash of the harness package itself (spike plan P5 pre-run item).

    Hashes every ``runners/killtest/*.py`` plus ``runners/run_killtest.py`` so a
    changed harness yields a changed version hash recorded in the run log."""
    pkg = pathlib.Path(__file__).parent
    files = sorted(pkg.rglob("*.py"))
    cli = paths.bench / "runners" / "run_killtest.py"
    if cli.exists():
        files.append(cli)
    lines = []
    for f in files:
        lines.append(f"{f.name}\0{hash_file(f)}")
    return hash_bytes("\n".join(lines).encode("utf-8"))


@dataclass
class Provenance:
    """The frozen-document fingerprints stamped into every run log (G3 + P5)."""

    prereg_version: str = PREREG_VERSION
    prereg_sha256: str = ""
    registry_sha256: str = ""
    harness_version_sha256: str = ""
    hash_algo: str = HASH_ALGO
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def capture(cls, paths: Paths) -> "Provenance":
        return cls(
            prereg_sha256=prereg_hash(paths),
            registry_sha256=registry_hash(paths),
            harness_version_sha256=harness_version_hash(paths),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "prereg_version": self.prereg_version,
            "prereg_sha256": self.prereg_sha256,
            "registry_sha256": self.registry_sha256,
            "harness_version_sha256": self.harness_version_sha256,
            "hash_algo": self.hash_algo,
            **self.extra,
        }


# ----------------------------------------------------------------- task packs (v1)
#
# A TaskPack bundles every per-task frozen value so a new task (Stage-1) can be
# added WITHOUT editing the v0 SortedUniqList constants in place. The v0 pack is
# built FROM the module-level constants above (single source of truth, so v0 stays
# byte-identical); the stage1 pack carries its own ratified Stage-1 values. Select
# with the env var KILLTEST_PACK ("v0" default | "stage1").

@dataclass(frozen=True)
class TaskPack:
    pack_id: str
    prereg_version: str
    prereg_filename: str
    cap: int
    operations: tuple[str, ...]
    laws: tuple[str, ...]
    n_per_arm: int
    model_id_pinned: str
    # Approved model substitutes (prereg v1.1 amendment §5). The checklist accepts
    # a recorded model_id that matches the pin OR one of these; empty for v0.
    model_substitutes: tuple[str, ...]
    private_subdir: str          # subdir under ~/tao-killtest-private ("" = root)
    mutation_specs: str          # selector consumed by mutation.specs_for()
    r1_median_factor: float
    r2_p90_factor: float
    no_harm_allowance: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "pack_id": self.pack_id,
            "prereg_version": self.prereg_version,
            "prereg_filename": self.prereg_filename,
            "cap": self.cap,
            "operations": list(self.operations),
            "laws": list(self.laws),
            "n_per_arm": self.n_per_arm,
            "model_id_pinned": self.model_id_pinned,
            "model_substitutes": list(self.model_substitutes),
            "private_subdir": self.private_subdir,
            "mutation_specs": self.mutation_specs,
            "thresholds": {
                "R1_median_factor": self.r1_median_factor,
                "R2_p90_factor": self.r2_p90_factor,
                "no_harm_allowance": self.no_harm_allowance,
            },
        }


# v0 — frozen SortedUniqList pack, mirrored from the module constants (unchanged).
V0_PACK = TaskPack(
    pack_id="v0",
    prereg_version=PREREG_VERSION,
    prereg_filename="tao-killtest-prereg-v0.md",
    cap=CAP,
    operations=OPERATIONS,
    laws=LAWS,
    n_per_arm=N_PER_ARM,
    model_id_pinned=MODEL_ID_PINNED,
    model_substitutes=(),
    private_subdir="",
    mutation_specs="v0",
    r1_median_factor=R1_MEDIAN_FACTOR,
    r2_p90_factor=R2_P90_FACTOR,
    no_harm_allowance=NO_HARM_ALLOWANCE,
)

# stage1 — bounded relational mini-store (prereg v1, RATIFIED 2026-06-14). The
# target edit is `report`; `dashboard` is the A5a verified consumer. Same decision
# thresholds as v0 (R1 0.7 / R2 0.8 / no-harm 0.10). model_substitutes carries the
# v1.1 amendment substitute recorded at first run (left empty until ratified; the
# checklist also accepts a per-run recorded substitute).
STAGE1_PACK = TaskPack(
    pack_id="stage1",
    prereg_version="tao-killtest-prereg-v1-stage1",
    prereg_filename="tao-killtest-prereg-v1-stage1.md",
    cap=64,
    operations=("report", "dashboard"),
    laws=("L-validonly", "L-join", "L-group", "L-sum-bounded", "L-sortuniq"),
    n_per_arm=5,
    model_id_pinned=MODEL_ID_PINNED,
    model_substitutes=(),
    private_subdir="stage1",
    mutation_specs="stage1",
    r1_median_factor=R1_MEDIAN_FACTOR,
    r2_p90_factor=R2_P90_FACTOR,
    no_harm_allowance=NO_HARM_ALLOWANCE,
)

PACKS: dict[str, TaskPack] = {p.pack_id: p for p in (V0_PACK, STAGE1_PACK)}


def active_pack(name: str | None = None) -> TaskPack:
    """Select the task pack by explicit name, else env KILLTEST_PACK, else v0."""
    key = name or os.environ.get("KILLTEST_PACK", "v0")
    if key not in PACKS:
        raise SystemExit(f"unknown KILLTEST_PACK {key!r} (have: {sorted(PACKS)})")
    return PACKS[key]
