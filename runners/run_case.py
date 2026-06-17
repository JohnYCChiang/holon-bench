#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import tempfile
import time

from common import (
    apply_artifact_file,
    apply_patch_file,
    bench_root,
    derive_unsafe_path_failure,
    diff_analysis,
    find_case,
    git_changed_files,
    run_command,
    run_semantic_checks,
    scope_check,
    verifier_strength,
    write_json,
)


def ensure_git_repo(workspace: pathlib.Path) -> None:
    if (workspace / ".git").exists():
        baseline = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(workspace),
            text=True,
            capture_output=True,
            check=False,
        )
        if baseline.stdout.strip():
            subprocess.run(["git", "add", "-A"], cwd=str(workspace), check=True, capture_output=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Holon Bench",
                    "-c",
                    "user.email=bench@holon.local",
                    "commit",
                    "-m",
                    "fixture materialized",
                ],
                cwd=str(workspace),
                check=True,
                capture_output=True,
            )
        return
    subprocess.run(["git", "init"], cwd=str(workspace), check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=str(workspace), check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.name=Holon Bench", "-c", "user.email=bench@holon.local", "commit", "-m", "fixture"],
        cwd=str(workspace),
        check=True,
        capture_output=True,
    )


def materialize_fixture(root: pathlib.Path, fixture: str, work_root: pathlib.Path) -> pathlib.Path:
    source = root / fixture
    if not source.exists():
        raise SystemExit(f"fixture does not exist yet: {source}")
    workspace = work_root / source.name
    shutil.copytree(source, workspace)
    ensure_git_repo(workspace)
    return workspace


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_id")
    parser.add_argument("--model", required=True)
    submission = parser.add_mutually_exclusive_group(required=True)
    submission.add_argument("--patch-file")
    submission.add_argument("--artifact-file")
    parser.add_argument("--bench-root", default=".")
    parser.add_argument("--work-root")
    parser.add_argument("--out", default="reports/case_result.json")
    args = parser.parse_args()

    root = bench_root(args.bench_root)
    case = find_case(root, args.case_id)
    submission_file = pathlib.Path(args.patch_file or args.artifact_file).resolve()
    work_parent = pathlib.Path(args.work_root).resolve() if args.work_root else pathlib.Path(tempfile.mkdtemp(prefix="holon-bench-"))
    started = time.time()

    workspace = materialize_fixture(root, case["fixture"], work_parent)
    protocol = "patch" if args.patch_file else "artifact"
    patch_result = (
        apply_patch_file(workspace, submission_file)
        if protocol == "patch"
        else apply_artifact_file(workspace, submission_file, case.get("solution_paths", []))
    )
    generation_trace = load_generation_trace(submission_file)
    commands = []
    hidden_commands = []
    mutation_commands = []
    if patch_result["patch_applies"]:
        timeout = int(case["verifier"].get("timeout_seconds", 120))
        for command in case["verifier"]["commands"]:
            commands.append(run_command(command, workspace, timeout))
        for command in case["verifier"].get("hidden_commands", []) or []:
            hidden_commands.append(run_command(command, workspace, timeout))
        for command in case["verifier"].get("mutation_commands", []) or []:
            mutation_commands.append(run_command(command, workspace, timeout))

    changed = git_changed_files(workspace)
    diff = diff_analysis(workspace, changed) if changed else {
        "added_test_count": 0,
        "added_assertion_count": 0,
        "changed_test_files": [],
        "has_regression_test_signal": False,
        "added_test_lines": [],
    }
    scope = scope_check(
        changed,
        case["allowed_paths"],
        case["forbidden_paths"],
        case.get("protected_paths", []),
    )
    tests_pass = bool(commands) and all(cmd["exit_code"] == 0 and not cmd["timed_out"] for cmd in commands)
    hidden_pass = all(
        cmd["exit_code"] == 0 and not cmd["timed_out"] for cmd in hidden_commands
    )
    mutation_pass = all(
        cmd["exit_code"] == 0 and not cmd["timed_out"] for cmd in mutation_commands
    )
    semantic = run_semantic_checks(
        workspace,
        case.get("verifier", {}).get("semantic_checks", []),
        commands,
        generation_trace,
    )
    compile_failed = any(
        "could not compile" in cmd.get("stderr", "")
        or "compilation failed" in cmd.get("stderr", "").lower()
        for cmd in commands
    )
    compiles = patch_result["patch_applies"] and bool(commands) and not compile_failed

    failure_tags = []
    if not patch_result["patch_applies"]:
        failure_tags.append("patch_apply_failed" if protocol == "patch" else "invalid_artifact_output")
    if not patch_result.get("strict_output_contract_pass", patch_result["output_contract_pass"]):
        if protocol == "patch" or patch_result.get("artifact_paths"):
            failure_tags.append("extra_text")
    if patch_result["patch_applies"] and patch_result["output_contract_pass"] and not changed:
        failure_tags.append("missing_requirement")
    if not scope["scope_pass"]:
        if scope["protected_hits"]:
            failure_tags.append("test_tampering")
        elif scope["forbidden_hits"]:
            failure_tags.append("forbidden_file_touched")
        else:
            failure_tags.append("over_refactor")
    if compile_failed:
        failure_tags.append("compile_fail")
    elif commands and not tests_pass:
        failure_tags.append("test_fail")
    if any(cmd.get("timed_out") for cmd in commands):
        failure_tags.append("timeout")
    if not hidden_pass:
        failure_tags.append("hidden_verifier_failed")
    if not mutation_pass:
        failure_tags.append("mutation_verifier_failed")
    if not semantic["semantic_pass"]:
        failed_graph_checks = [
            item
            for item in semantic.get("checks", [])
            if item.get("check") in {"graph_context_used", "graph_relation_used", "project_scoped_graph_context"}
            and not item.get("passed")
        ]
        if any(not item.get("graph_tool_called") for item in failed_graph_checks):
            failure_tags.append("graph_tool_not_called")
        elif failed_graph_checks:
            failure_tags.append("graph_context_not_used")
        else:
            failure_tags.append("semantic_check_failed")
    if (
        derive_unsafe_path_failure(
            case.get("failure_tags", []),
            patch_applies=patch_result["patch_applies"],
            schema_valid=patch_result["output_contract_pass"],
            compiles=compiles,
            scope_pass=scope["scope_pass"],
            tests_pass=tests_pass,
            hidden_pass=hidden_pass,
            mutation_pass=mutation_pass,
        )
        and "unsafe_path" not in failure_tags
    ):
        failure_tags.append("unsafe_path")

    result = {
        "case_id": case["id"],
        "track": case["track"],
        "task_type": case["task_type"],
        "model": args.model,
        "protocol": protocol,
        "workspace": str(workspace),
        "duration_seconds": round(time.time() - started, 3),
        "generation_path": generation_trace.get("generation_path"),
        "fallback_used": generation_trace.get("fallback_used"),
        "workflow_attempted": generation_trace.get("workflow_attempted"),
        "workflow_type": generation_trace.get("workflow_type"),
        "governance_level": generation_trace.get("governance_level"),
        "governance_mode": generation_trace.get("governance_mode"),
        "governance_checks": generation_trace.get("governance_checks"),
        "prompt_stack": generation_trace.get("prompt_stack"),
        "tao_truth_chain": generation_trace.get("tao_truth_chain"),
        "changed_files": changed,
        "diff_analysis": diff,
        "commands": commands,
        "hidden_commands": hidden_commands,
        "mutation_commands": mutation_commands,
        "semantic_checks": semantic,
        "verifier_strength": verifier_strength(case),
        "generation_trace": generation_trace,
        "submission": patch_result,
        "scope": scope,
        "hard_gates": {
            "patch_applies": patch_result["patch_applies"],
            "compiles": compiles,
            "tests_pass": tests_pass,
            "schema_valid": patch_result["output_contract_pass"],
            "scope_pass": scope["scope_pass"],
            "safety_pass": "unsafe_path" not in failure_tags,
            "semantic_pass": semantic["semantic_pass"],
            "hidden_pass": hidden_pass,
            "mutation_pass": mutation_pass,
        },
        "failure_tags": failure_tags,
    }
    out = root / args.out
    write_json(out, result)
    print(out)
    return 0 if all(result["hard_gates"].values()) else 1


def load_generation_trace(submission_file: pathlib.Path) -> dict:
    meta_path = submission_file.with_suffix(submission_file.suffix + ".meta.json")
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        return {"trace_parse_error": str(err)}


if __name__ == "__main__":
    raise SystemExit(main())
