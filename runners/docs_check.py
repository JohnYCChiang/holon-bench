#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

from common import bench_root


RUNNER_COMMAND = re.compile(r"^python3 runners/(run_track\.py|run_case\.py)\b")
FLAG = re.compile(r"--[a-z0-9][a-z0-9-]*")
DEPRECATED_DOC_FLAGS = {"--repair-budget"}


def runner_flags(root: pathlib.Path, runner: str) -> set[str]:
    completed = subprocess.run(
        [sys.executable, str(root / "runners" / runner), "--help"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"{runner} --help failed:\n{completed.stderr}")
    return set(FLAG.findall(completed.stdout))


def markdown_commands(path: pathlib.Path) -> list[tuple[int, str, str]]:
    commands: list[tuple[int, str, str]] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        match = RUNNER_COMMAND.match(stripped)
        if not match:
            index += 1
            continue
        start = index + 1
        parts = [stripped.removesuffix("\\").strip()]
        while stripped.endswith("\\") and index + 1 < len(lines):
            index += 1
            stripped = lines[index].strip()
            parts.append(stripped.removesuffix("\\").strip())
        commands.append((start, match.group(1), " ".join(parts)))
        index += 1
    return commands


def main() -> int:
    root = bench_root(sys.argv[1] if len(sys.argv) > 1 else ".")
    docs = [
        root / "README.md",
        *sorted((root / "docs").rglob("*.md")),
        *sorted((root / "reports").glob("*.md")),
    ]
    known_flags = {
        "run_track.py": runner_flags(root, "run_track.py"),
        "run_case.py": runner_flags(root, "run_case.py"),
    }
    errors: list[str] = []

    for path in docs:
        if not path.exists():
            continue
        for line, runner, command in markdown_commands(path):
            command_flags = set(FLAG.findall(command))
            deprecated = sorted(command_flags & DEPRECATED_DOC_FLAGS)
            if deprecated:
                errors.append(
                    f"{path.relative_to(root)}:{line}: deprecated command flags {deprecated}"
                )
            unknown = sorted(command_flags - known_flags[runner])
            if unknown:
                errors.append(
                    f"{path.relative_to(root)}:{line}: {runner} unknown flags {unknown}"
                )

    track_flags = known_flags["run_track.py"]
    for required in ("--repair-attempts", "--repair-budget"):
        if required not in track_flags:
            errors.append(f"run_track.py --help missing expected flag {required}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("docs_check: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
