#!/usr/bin/env python3
"""Offline stand-in for the Holon CLI, used by the Holon smoke path and tests.

The real Holon driver shells out to a compiled ``holon`` binary that performs
model calls and edits the workspace. That binary is unavailable in CI and would
require remote APIs. This stub mimics only the parts of the Holon contract the
benchmark driver depends on:

- it edits an owned file in the workspace (deterministically), so the driver can
  collect a normalized artifact/diff exactly as it would from real Holon output;
- when asked, it writes ``.holon/governance.json`` with the optional governance
  metadata (governance_mode / governance_checks / tao_truth_chain) that the
  driver surfaces "when present";
- it prints a Holon-style JSON trace line so graph-tool detection has input.

It performs no network or model calls. Behavior is driven entirely by env vars
so the stub stays case-agnostic:

- ``HOLON_STUB_TARGET``      workspace-relative file to edit (required to edit)
- ``HOLON_STUB_MARKER``      text inserted into the target (default: a comment)
- ``HOLON_STUB_ANCHOR``      if set, marker is inserted before this text;
                             otherwise the marker is prepended to the file
- ``HOLON_STUB_GOVERNANCE``  ``"1"`` to emit ``.holon/governance.json``
- ``HOLON_STUB_CASE``        case id recorded in the tao_truth_chain subject id
"""
from __future__ import annotations

import json
import os
import pathlib
import sys


def apply_change(cwd: pathlib.Path) -> None:
    target = os.environ.get("HOLON_STUB_TARGET")
    if not target:
        return
    path = cwd / target
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    marker = os.environ.get("HOLON_STUB_MARKER", "# holon offline stub change\n")
    if marker in text:
        return
    anchor = os.environ.get("HOLON_STUB_ANCHOR")
    if anchor and anchor in text:
        text = text.replace(anchor, marker + anchor, 1)
    else:
        text = marker + text
    path.write_text(text, encoding="utf-8")


def write_governance(cwd: pathlib.Path) -> None:
    if os.environ.get("HOLON_STUB_GOVERNANCE") != "1":
        return
    case_id = os.environ.get("HOLON_STUB_CASE", "smoke")
    holon_dir = cwd / ".holon"
    holon_dir.mkdir(exist_ok=True)
    governance = {
        "governance_mode": "governed",
        "governance_checks": [
            {
                "name": "scope_guard",
                "passed": True,
                "tao_fact_id": f"fact-scope-{case_id}",
                "detail": "edits stayed within allowed paths",
            },
            {
                "name": "verifier_gate",
                "passed": True,
                "detail": "verifier was run, not bypassed",
            },
        ],
        "tao_truth_chain": {
            "subject_id": f"case::{case_id}",
            "fact_kind": "implementation",
            "fact_id": f"fact-impl-{case_id}",
            "artifact_ids": [f"artifact-{case_id}"],
            "verifier_input_ids": [f"verifier-{case_id}"],
        },
    }
    (holon_dir / "governance.json").write_text(
        json.dumps(governance, indent=2), encoding="utf-8"
    )


def main() -> int:
    cwd = pathlib.Path.cwd()
    apply_change(cwd)
    write_governance(cwd)
    # Holon-style trace line so the driver's graph-tool detection has input.
    print(json.dumps({"graph_tool_calls": ["RecallMemory"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
