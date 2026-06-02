#!/usr/bin/env python3
from __future__ import annotations

import fnmatch
import json
import os
import pathlib
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Any

import yaml


BENCH_ROOT_MARKER = "manifest/benchmark.yaml"


def bench_root(path: str | os.PathLike[str] | None = None) -> pathlib.Path:
    root = pathlib.Path(path or ".").resolve()
    if root.is_file():
        root = root.parent
    while root != root.parent:
        if (root / BENCH_ROOT_MARKER).exists():
            return root
        root = root.parent
    raise SystemExit(f"could not find benchmark root containing {BENCH_ROOT_MARKER}")


def load_yaml(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def write_json(path: pathlib.Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def load_cases(root: pathlib.Path) -> list[dict[str, Any]]:
    benchmark = load_yaml(root / "manifest/benchmark.yaml")
    cases: list[dict[str, Any]] = []
    for rel in benchmark["case_files"]:
        case_file = load_yaml(root / rel)
        for case in case_file.get("cases", []):
            cases.append(case)
    return cases


def find_case(root: pathlib.Path, case_id: str) -> dict[str, Any]:
    for case in load_cases(root):
        if case["id"] == case_id:
            return case
    raise SystemExit(f"case not found: {case_id}")


def run_command(command: str, cwd: pathlib.Path, timeout: int) -> dict[str, Any]:
    started = time.time()
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.setdefault("GOCACHE", "/tmp/holon-bench-go-cache")
    env.setdefault("GOMODCACHE", "/tmp/holon-bench-go-mod-cache")
    env.setdefault("GOPATH", "/tmp/holon-bench-go-path")
    env.setdefault("CARGO_TARGET_DIR", "/tmp/holon-bench-cargo-target")
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout,
            env=env,
        )
        return {
            "command": command,
            "exit_code": completed.returncode,
            "timed_out": False,
            "duration_seconds": round(time.time() - started, 3),
            "stdout": completed.stdout[-8000:],
            "stderr": completed.stderr[-8000:],
        }
    except subprocess.TimeoutExpired as err:
        return {
            "command": command,
            "exit_code": None,
            "timed_out": True,
            "duration_seconds": round(time.time() - started, 3),
            "stdout": (err.stdout or "")[-8000:] if isinstance(err.stdout, str) else "",
            "stderr": (err.stderr or "")[-8000:] if isinstance(err.stderr, str) else "",
        }


def git_changed_files(cwd: pathlib.Path) -> list[str]:
    tracked = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )
    if tracked.returncode != 0 or untracked.returncode != 0:
        return []
    changed = set(tracked.stdout.splitlines()) | set(untracked.stdout.splitlines())
    return sorted(line.strip() for line in changed if line.strip())


def diff_analysis(cwd: pathlib.Path, changed_files: list[str]) -> dict[str, Any]:
    diff = subprocess.run(
        ["git", "diff", "--unified=0", "--", *changed_files],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )
    added_test_lines: list[str] = []
    added_assertions: list[str] = []
    for line in diff.stdout.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        added = line[1:].strip()
        if looks_like_test_declaration(added):
            added_test_lines.append(added[:240])
        if looks_like_assertion(added):
            added_assertions.append(added[:240])

    changed_test_files = [
        path
        for path in changed_files
        if "/tests/" in f"/{path}" or pathlib.Path(path).name.startswith("test_")
    ]
    return {
        "added_test_count": len(added_test_lines),
        "added_assertion_count": len(added_assertions),
        "changed_test_files": changed_test_files,
        "has_regression_test_signal": bool(added_test_lines or added_assertions or changed_test_files),
        "added_test_lines": added_test_lines[:20],
    }


def looks_like_test_declaration(line: str) -> bool:
    return (
        line == "#[test]"
        or line.startswith("def test_")
        or line.startswith("async def test_")
        or line.startswith("func Test")
        or line.startswith("test(")
        or line.startswith("testWidgets(")
        or "@Test" in line
    )


def looks_like_assertion(line: str) -> bool:
    return (
        line.startswith("assert ")
        or line.startswith("assert!(")
        or line.startswith("assert_eq!(")
        or line.startswith("assert_ne!(")
        or line.startswith("self.assert")
        or line.startswith("require.")
        or line.startswith("assert.")
        or line.startswith("expect(")
    )


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def scope_check(
    changed_files: list[str],
    allowed: list[str],
    forbidden: list[str],
    protected: list[str] | None = None,
) -> dict[str, Any]:
    protected = protected or []
    forbidden_hits = [path for path in changed_files if matches_any(path, forbidden)]
    protected_hits = [path for path in changed_files if matches_any(path, protected)]
    outside_allowed = [path for path in changed_files if not matches_any(path, allowed)]
    return {
        "scope_pass": not forbidden_hits and not protected_hits and not outside_allowed,
        "forbidden_hits": forbidden_hits,
        "protected_hits": protected_hits,
        "outside_allowed": outside_allowed,
    }


def run_semantic_checks(
    workspace: pathlib.Path,
    checks: list[str] | None,
    commands: list[dict[str, Any]],
    generation_trace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    checks = checks or []
    generation_trace = generation_trace or {}
    results = []
    for check in checks:
        if check == "no_dart_io_in_web_path":
            result = semantic_no_forbidden_import(
                workspace,
                extensions={".dart"},
                needles={"dart:io"},
                roots=("lib",),
            )
        elif check == "wasm_compatibility_scan":
            result = semantic_no_forbidden_import(
                workspace,
                extensions={".rs"},
                needles={"std::fs", "std::process", "std::os::unix", "std::os::windows"},
                roots=("src",),
            )
        elif check == "golden_layout_bounds":
            result = {
                "check": check,
                "passed": commands_passed(commands)
                and not command_output_contains(commands, {"overflowed by", "RenderFlex overflowed"}),
                "details": "widget verifier output contained no Flutter overflow marker",
            }
        elif check.startswith("python_rust_") or check.startswith("golden_hash_"):
            result = {
                "check": check,
                "passed": commands_passed(commands),
                "details": "semantic parity is enforced by the fixture verifier commands",
            }
        elif check in {
            "graph_context_used",
            "graph_relation_used",
            "project_scoped_graph_context",
        }:
            called_tools = set(generation_trace.get("called_tools", []))
            graph_tool_called = bool(
                called_tools
                & {"RecallMemory", "QueryKnowledge", "TraverseKnowledge", "VerifyConstraints"}
            )
            verifier_passed = commands_passed(commands)
            result = {
                "check": check,
                "passed": verifier_passed and graph_tool_called,
                "graph_tool_called": graph_tool_called,
                "verifier_passed": verifier_passed,
                "details": (
                    "hidden verifier passed and graph tool call was observed"
                    if verifier_passed and graph_tool_called
                    else "graph tool call was observed, but hidden verifier failed"
                    if graph_tool_called
                    else "hidden verifier may pass, but no graph tool call was observed"
                ),
            }
        else:
            result = {
                "check": check,
                "passed": False,
                "details": "unknown semantic check",
            }
        results.append(result)
    return {
        "semantic_pass": all(item["passed"] for item in results),
        "checks": results,
    }


def verifier_strength(case: dict[str, Any]) -> dict[str, Any]:
    verifier = case.get("verifier", {})
    commands = verifier.get("commands", []) or []
    hidden_commands = verifier.get("hidden_commands", []) or []
    mutation_commands = verifier.get("mutation_commands", []) or []
    all_commands = [*commands, *hidden_commands, *mutation_commands]
    semantic_checks = verifier.get("semantic_checks", []) or []
    protected_paths = case.get("protected_paths", []) or []
    hard_gates = case.get("scoring", {}).get("hard_gates", []) or []
    has_hidden_path = any(
        path.startswith("hidden/")
        or "/hidden/" in path
        or path.startswith("python/")
        or path.startswith("golden/")
        or path.startswith("rust/tests/")
        or path.startswith("tests/")
        or path.startswith("test/")
        or "/tests/" in path
        or "/test/" in path
        or "/*_test." in path
        or path.endswith("_test.go")
        or path.endswith("_test.rs")
        or path.endswith("_test.dart")
        or pathlib.Path(path).name.startswith("test_")
        for path in protected_paths
    )
    command_text = "\n".join(all_commands)
    has_hidden_command = bool(hidden_commands) or " hidden/" in f" {command_text}" or "/hidden/" in command_text
    has_mutation_command = bool(mutation_commands)
    score = 0
    if commands:
        score += 2
    if protected_paths:
        score += 2
    if has_hidden_path or has_hidden_command:
        score += 2
    if has_mutation_command:
        score += 2
    if semantic_checks:
        score += 2
    if "scope_pass" in hard_gates:
        score += 1
    if "safety_pass" in hard_gates:
        score += 1
    if "semantic_pass" in hard_gates:
        score += 1
    if len(all_commands) > 1:
        score += 1

    if score >= 9:
        tier = "strong"
    elif score >= 6:
        tier = "standard"
    else:
        tier = "basic"

    return {
        "tier": tier,
        "score": score,
        "has_verifier_commands": bool(commands),
        "verifier_command_count": len(commands),
        "hidden_command_count": len(hidden_commands),
        "mutation_command_count": len(mutation_commands),
        "has_protected_paths": bool(protected_paths),
        "protected_path_count": len(protected_paths),
        "has_hidden_verifier": bool(has_hidden_path or has_hidden_command),
        "has_mutation_verifier": has_mutation_command,
        "has_semantic_checks": bool(semantic_checks),
        "semantic_checks": semantic_checks,
        "hard_gates": hard_gates,
        "scope_gate_declared": "scope_pass" in hard_gates,
        "safety_gate_declared": "safety_pass" in hard_gates,
        "semantic_gate_declared": "semantic_pass" in hard_gates,
    }


def commands_passed(commands: list[dict[str, Any]]) -> bool:
    return bool(commands) and all(
        command.get("exit_code") == 0 and not command.get("timed_out")
        for command in commands
    )


def command_output_contains(commands: list[dict[str, Any]], needles: set[str]) -> bool:
    for command in commands:
        combined = f"{command.get('stdout', '')}\n{command.get('stderr', '')}"
        if any(needle in combined for needle in needles):
            return True
    return False


def semantic_no_forbidden_import(
    workspace: pathlib.Path,
    *,
    extensions: set[str],
    needles: set[str],
    roots: tuple[str, ...],
) -> dict[str, Any]:
    hits: list[str] = []
    for root_name in roots:
        root = workspace / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in extensions:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for line in semantic_scan_lines(path, text):
                for needle in needles:
                    if needle in line:
                        hits.append(f"{path.relative_to(workspace)}:{needle}")
    return {
        "check": "forbidden_import_scan",
        "passed": not hits,
        "details": "no forbidden imports found" if not hits else "; ".join(hits[:20]),
    }


def semantic_scan_lines(path: pathlib.Path, text: str) -> list[str]:
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("//", "///", "/*", "*", "#")):
            continue
        if path.suffix == ".dart" and not line.startswith(("import ", "export ")):
            continue
        lines.append(line)
    return lines


def extract_patch(raw: str) -> str:
    if "```diff" in raw:
        start = raw.find("```diff")
        after_open = raw.find("\n", start) + 1
        end = raw.find("```", after_open)
        if end != -1:
            return raw[after_open:end].rstrip("\r\n") + "\n"
    if "```patch" in raw:
        start = raw.find("```patch")
        after_open = raw.find("\n", start) + 1
        end = raw.find("```", after_open)
        if end != -1:
            return raw[after_open:end].rstrip("\r\n") + "\n"
    return raw.rstrip("\r\n") + "\n"


def apply_patch_file(workspace: pathlib.Path, patch_file: pathlib.Path) -> dict[str, Any]:
    raw = patch_file.read_text(encoding="utf-8")
    normalized = raw.rstrip("\r\n")
    output_contract_pass = normalized.startswith("diff --git ") or normalized.startswith("--- a/")
    patch = extract_patch(raw)
    temp_patch = workspace / ".holon_bench_model.patch"
    temp_patch.write_text(patch, encoding="utf-8")
    completed = subprocess.run(
        ["git", "apply", "--whitespace=nowarn", str(temp_patch)],
        cwd=str(workspace),
        text=True,
        capture_output=True,
        check=False,
    )
    temp_patch.unlink(missing_ok=True)
    return {
        "patch_applies": completed.returncode == 0,
        "output_contract_pass": output_contract_pass,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def apply_artifact_file(
    workspace: pathlib.Path, artifact_file: pathlib.Path, solution_paths: list[str]
) -> dict[str, Any]:
    import re

    raw = artifact_file.read_text(encoding="utf-8")
    contract_raw = raw.strip()
    header = "--- FILE: "
    strict_contract_pass = contract_raw.startswith(header) and not contract_raw.endswith("```")

    match = re.search(r"--- FILE: .*? ---", raw)
    recovered = False
    if match:
        recovered = match.start() != 0
        raw = raw[match.start():]
    raw = raw.strip()

    files: dict[str, str] = {}
    current: str | None = None
    body: list[str] = []
    for line in raw.splitlines():
        header_match = re.search(r"--- FILE: (.*?) ---", line)
        if header_match:
            if current is not None:
                files[current] = clean_artifact_body("\n".join(body)) + "\n"
            current = header_match.group(1).strip()
            suffix = line[header_match.end():]
            body = [suffix] if suffix.strip() else []
            if header_match.start() != 0 or suffix.strip():
                recovered = True
        elif current is not None:
            body.append(line)
    if current is not None:
        files[current] = clean_artifact_body("\n".join(body)) + "\n"

    expected = set(solution_paths)
    if expected:
        extra = set(files) - expected
        placeholder_paths = {"relative/path", "path/to/file", "owned/file"}
        removable = {
            path
            for path in extra
            if path in placeholder_paths or path.startswith(("relative/", "path/to/"))
        }
        if removable:
            recovered = True
            for path in removable:
                files.pop(path, None)
    actual = set(files)
    paths_match = bool(files) and actual == expected
    strict_output_contract_pass = paths_match and strict_contract_pass and not recovered
    if not paths_match:
        return {
            "patch_applies": False,
            "output_contract_pass": False,
            "strict_output_contract_pass": False,
            "artifact_paths": sorted(actual),
            "stdout": "",
            "stderr": f"artifact output paths mismatch: expected {sorted(expected)}, got {sorted(actual)}",
        }
    for path, content in files.items():
        target = workspace / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return {
        "patch_applies": True,
        "output_contract_pass": True,
        "strict_output_contract_pass": strict_output_contract_pass,
        "recovered_output": recovered or not strict_output_contract_pass,
        "artifact_paths": sorted(actual),
        "stdout": "",
        "stderr": "" if strict_output_contract_pass else "artifact recovered from non-contract output",
    }


def clean_artifact_body(body: str) -> str:
    body = body.strip()
    if "\n" in body:
        first, rest = body.split("\n", 1)
        if first.strip().startswith("```"):
            body = rest.lstrip()
    elif body.startswith("```"):
        return ""
    if body.rstrip().endswith("```"):
        body = body.rstrip()[:-3].rstrip()
    return body
