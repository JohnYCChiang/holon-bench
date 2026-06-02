#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib

from common import bench_root, find_case, git_changed_files, scope_check


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_id")
    parser.add_argument("workspace")
    parser.add_argument("--bench-root", default=".")
    args = parser.parse_args()

    root = bench_root(args.bench_root)
    case = find_case(root, args.case_id)
    workspace = pathlib.Path(args.workspace).resolve()
    changed = git_changed_files(workspace)
    result = scope_check(
        changed,
        case["allowed_paths"],
        case["forbidden_paths"],
        case.get("protected_paths", []),
    )
    result["changed_files"] = changed
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["scope_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
