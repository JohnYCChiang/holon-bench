#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import signal
import shutil
import subprocess
import sys
import tempfile
import urllib.request

from common import bench_root, find_case


def fixture_context(root: pathlib.Path, fixture: str, max_chars: int) -> str:
    base = root / fixture
    if not base.exists():
        raise SystemExit(f"fixture does not exist: {base}")
    parts: list[str] = []
    length = 0
    for path in sorted(base.rglob("*")):
        if (
            not path.is_file()
            or ".git" in path.parts
            or ".holon" in path.parts
            or "__pycache__" in path.parts
            or "target" in path.parts
            or "hidden" in path.parts
            or ".bench" in path.parts
        ):
            continue
        rel = path.relative_to(base).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        block = f"\n--- FILE: {rel} ---\n{text}\n"
        if length + len(block) > max_chars:
            break
        parts.append(block)
        length += len(block)
    return "".join(parts)


def build_prompt(case: dict, files: str, protocol: str) -> str:
    constraints = "\n".join(f"- {item}" for item in case["constraints"])
    allowed = "\n".join(f"- {item}" for item in case["allowed_paths"])
    forbidden = "\n".join(f"- {item}" for item in case["forbidden_paths"])
    protected = "\n".join(f"- {item}" for item in case.get("protected_paths", [])) or "- none"
    if protocol == "patch":
        output_contract = """Return ONLY one unified git diff suitable for `git apply`. Do not use Markdown
fences and do not include explanation. Modify only allowed paths."""
    else:
        targets = "\n".join(f"- {path}" for path in case.get("solution_paths", []))
        output_contract = f"""Return ONLY complete owned file artifacts in this exact format:
--- FILE: relative/path ---
complete file content

Write exactly these owned files and no others:
{targets}
Do not use Markdown fences and do not include explanation."""

    return f"""You are the patch worker being benchmarked. Solve exactly one repository task.

{output_contract}

CASE ID: {case["id"]}
TASK:
{case["user_request"].strip()}

CONSTRAINTS:
{constraints}

ALLOWED PATHS:
{allowed}

FORBIDDEN PATHS:
{forbidden}

PROTECTED PATHS (read-only verifier assets; do not modify):
{protected}

TESTING EXPECTATION:
- Add focused regression/unit tests when they fit inside owned solution files or
  explicitly allowed test files.
- Do not modify protected verifier assets to make checks pass.

CURRENT FIXTURE FILES:
{files}
"""


def build_holon_cli_prompt(case: dict, files: str, protocol: str) -> str:
    constraints = "\n".join(f"- {item}" for item in case["constraints"])
    allowed = "\n".join(f"- {item}" for item in case["allowed_paths"])
    forbidden = "\n".join(f"- {item}" for item in case["forbidden_paths"])
    protected = "\n".join(f"- {item}" for item in case.get("protected_paths", [])) or "- none"
    targets = "\n".join(f"- {path}" for path in case.get("solution_paths", [])) or "- use the allowed paths"
    verifier_commands = "\n".join(f"- {command}" for command in case.get("verifier", {}).get("commands", [])) or "- none"
    return f"""You are the Holon CLI worker being benchmarked. Solve exactly one repository task.

Use your tools to modify the workspace files directly. Do not emit the final patch,
diff, or file artifact in chat; the benchmark runner will extract the result from
the workspace after tool execution.

Before responding DONE, run the verifier commands listed below when they are not
"none". If a verifier fails, inspect the error, modify only owned solution files,
and rerun the failing verifier. Respond DONE only after the verifier passes or
after you have a concrete blocker that cannot be fixed within the allowed files.

When the workspace changes are complete, stop calling tools and respond exactly:
DONE

CASE ID: {case["id"]}
TASK:
{case["user_request"].strip()}

CONSTRAINTS:
{constraints}

ALLOWED PATHS:
{allowed}

FORBIDDEN PATHS:
{forbidden}

PROTECTED PATHS (read-only verifier assets; do not modify):
{protected}

OWNED SOLUTION FILES:
{targets}

TESTING EXPECTATION:
- Add focused regression/unit tests when they fit inside owned solution files or
  explicitly allowed test files.
- Do not modify protected verifier assets to make checks pass.

VERIFIER COMMANDS:
{verifier_commands}

CURRENT FIXTURE FILES:
{files}
"""


def request_patch(
    endpoint: str,
    model: str,
    prompt: str,
    *,
    max_output_tokens: int | None = None,
    generation_timeout_seconds: float = 600.0,
    temperature: float = 0.1,
    top_p: float = 0.9,
    min_p: float | None = None,
    reasoning_budget: int | None = None,
    telemetry: dict | None = None,
) -> str:
    # Generation controls mirror Holon workflow fields: max_output_tokens maps to
    # the OpenAI-compatible `max_tokens` request field. temperature/top_p/min_p are
    # the sampling-profile controls; min_p is sent only when provided since not every
    # OpenAI-compatible endpoint accepts it. reasoning_budget mirrors the field the
    # Holon openai_compat provider sends to bound server-side reasoning tokens; it is
    # sent only when provided so default behavior is unchanged, and endpoints that do
    # not recognize it (it is a llama.cpp server extension) simply ignore it.
    body_payload: dict = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "top_p": top_p,
        "stream": False,
    }
    if min_p is not None:
        body_payload["min_p"] = min_p
    if reasoning_budget is not None:
        body_payload["reasoning_budget"] = reasoning_budget
    if max_output_tokens is not None:
        body_payload["max_tokens"] = max_output_tokens
    payload = json.dumps(body_payload).encode("utf-8")
    request = urllib.request.Request(
        endpoint.rstrip("/") + "/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=generation_timeout_seconds) as response:
        body = json.loads(response.read().decode("utf-8"))
    choice = body["choices"][0]
    if telemetry is not None:
        usage = body.get("usage") or {}
        finish_reason = choice.get("finish_reason")
        telemetry["max_output_tokens"] = max_output_tokens
        telemetry["max_tokens_in_request"] = max_output_tokens is not None
        telemetry["temperature"] = temperature
        telemetry["top_p"] = top_p
        telemetry["min_p"] = min_p
        telemetry["reasoning_budget"] = reasoning_budget
        telemetry["reasoning_budget_in_request"] = reasoning_budget is not None
        telemetry["prompt_tokens"] = usage.get("prompt_tokens")
        telemetry["completion_tokens"] = usage.get("completion_tokens")
        telemetry["finish_reason"] = finish_reason
        telemetry["truncated"] = finish_reason == "length"
    return choice["message"]["content"]


def _significant_line(line: str) -> str | None:
    """Return a normalized line if it is substantial enough to count toward the
    repetition guard, else None. Trivial structural lines (closing braces, short
    boilerplate) legitimately recur in code and must not trip the loop detector."""
    s = line.strip()
    if len(s) < 15:
        return None
    # need at least two word-ish tokens so `});`-type lines are excluded
    if sum(c.isalnum() for c in s) < 8:
        return None
    return s


def stream_request_patch(
    endpoint: str,
    model: str,
    prompt: str,
    *,
    solution_paths: list[str],
    max_output_tokens: int | None = None,
    generation_timeout_seconds: float = 600.0,
    temperature: float = 0.1,
    top_p: float = 0.9,
    min_p: float | None = None,
    reasoning_budget: int | None = None,
    repeat_threshold: int = 4,
    telemetry: dict | None = None,
) -> str:
    """Streaming variant of request_patch with content-side early stop.

    Mirrors the lever Holon actually has and the bench's blocking call lacks: it
    consumes the generation incrementally and cuts it off when the *content channel*
    shows rumination — either a second `--- FILE:` marker for a single-owned-file
    case (re-emission as a new block) or a substantial line repeating `repeat_threshold`
    times (re-emission as comments / a repetition loop). The non-streaming
    request_patch is left untouched; this path is opt-in.
    """
    body_payload: dict = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "top_p": top_p,
        "stream": True,
        "stream_options": {"include_usage": True},
    }
    if min_p is not None:
        body_payload["min_p"] = min_p
    if reasoning_budget is not None:
        body_payload["reasoning_budget"] = reasoning_budget
    if max_output_tokens is not None:
        body_payload["max_tokens"] = max_output_tokens
    payload = json.dumps(body_payload).encode("utf-8")
    request = urllib.request.Request(
        endpoint.rstrip("/") + "/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    single_owned = len(solution_paths) == 1
    marker = "--- FILE: "
    buf: list[str] = []
    pending = ""           # current not-yet-newline-terminated line fragment
    line_counts: dict[str, int] = {}
    completion_tokens = None
    server_finish = None
    early_stop = None

    def full() -> str:
        return "".join(buf) + pending

    with urllib.request.urlopen(request, timeout=generation_timeout_seconds) as response:
        for raw in response:
            line = raw.decode("utf-8", "replace").strip()
            if not line or not line.startswith("data:"):
                continue
            data = line[len("data:"):].strip()
            if data == "[DONE]":
                break
            try:
                chunk = json.loads(data)
            except json.JSONDecodeError:
                continue
            usage = chunk.get("usage")
            if usage:
                completion_tokens = usage.get("completion_tokens", completion_tokens)
            choices = chunk.get("choices") or []
            if not choices:
                continue
            ch0 = choices[0]
            if ch0.get("finish_reason"):
                server_finish = ch0["finish_reason"]
            delta = (ch0.get("delta") or {}).get("content")
            if not delta:
                continue
            # assemble lines incrementally
            pending += delta
            while "\n" in pending:
                ln, pending = pending.split("\n", 1)
                buf.append(ln + "\n")
                sig = _significant_line(ln)
                if sig is not None:
                    line_counts[sig] = line_counts.get(sig, 0) + 1
                    if line_counts[sig] >= repeat_threshold:
                        early_stop = "repetition"
                        break
            if early_stop:
                break
            # second FILE marker for a single-owned-file case => re-emission
            if single_owned and full().count(marker) >= 2:
                early_stop = "dup_file_marker"
                # drop everything from the 2nd marker onward
                whole = full()
                cut = whole.find(marker, whole.find(marker) + len(marker))
                return _finalize_stream(
                    whole[:cut], telemetry, temperature, top_p, min_p, reasoning_budget,
                    max_output_tokens, completion_tokens, server_finish, early_stop,
                )

    return _finalize_stream(
        full(), telemetry, temperature, top_p, min_p, reasoning_budget,
        max_output_tokens, completion_tokens, server_finish, early_stop,
    )


def _finalize_stream(content, telemetry, temperature, top_p, min_p, reasoning_budget,
                     max_output_tokens, completion_tokens, server_finish, early_stop):
    if telemetry is not None:
        finish_reason = early_stop or server_finish
        telemetry["max_output_tokens"] = max_output_tokens
        telemetry["max_tokens_in_request"] = max_output_tokens is not None
        telemetry["temperature"] = temperature
        telemetry["top_p"] = top_p
        telemetry["min_p"] = min_p
        telemetry["reasoning_budget"] = reasoning_budget
        telemetry["reasoning_budget_in_request"] = reasoning_budget is not None
        telemetry["completion_tokens"] = completion_tokens
        telemetry["finish_reason"] = finish_reason
        telemetry["early_stopped"] = early_stop is not None
        telemetry["early_stop_reason"] = early_stop
        # a run we cut off content-side is NOT a budget-truncated failure
        telemetry["truncated"] = (early_stop is None) and (server_finish == "length")
        telemetry["streaming"] = True
    return content


def append_repair_feedback(prompt: str, previous_artifact: str | None, feedback_error: str | None) -> str:
    if not previous_artifact or not feedback_error:
        return prompt
    prev_path = pathlib.Path(previous_artifact).resolve()
    if not prev_path.exists():
        return prompt
    prev_content = prev_path.read_text(encoding="utf-8")
    return (
        f"{prompt}\n\n--- PREVIOUS DRAFT ---\n{prev_content}\n\n"
        "Your previous submission failed compilation or verification checks.\n"
        f"Here is the stdout/stderr diagnostic:\n{feedback_error}\n\n"
        "Repair contract:\n"
        "- Treat the previous draft as the starting point; make the smallest sufficient correction.\n"
        "- Preserve behavior that was already correct in the previous draft.\n"
        "- If there is a compile/type error, fix that before changing semantics.\n"
        "- If tests fail after compilation, map each failing assertion to the smallest code change that satisfies it.\n"
        "- Do not add files, dependencies, shell wrappers, broad rewrites, or unrelated abstractions.\n"
        "- Return only the corrected complete owned file artifact and still obey the original output contract."
    )


def ensure_git_repo(workspace: pathlib.Path) -> None:
    if (workspace / ".git").exists():
        return
    subprocess.run(["git", "init"], cwd=workspace, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    subprocess.run(["git", "config", "user.name", "bench"], cwd=workspace, check=True)
    subprocess.run(["git", "config", "user.email", "bench@holon"], cwd=workspace, check=True)
    subprocess.run(["git", "add", "."], cwd=workspace, check=True)
    subprocess.run(
        ["git", "commit", "-m", "initial fixture"],
        cwd=workspace,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


def generation_fixture_ignore(_directory: str, names: list[str]) -> set[str]:
    ignored = {".git", ".holon", "__pycache__", "target", "bench_prompt.txt", ".bench"}
    return {name for name in names if name in ignored or name == "hidden"}


def run_process_group(
    command: list[str],
    *,
    cwd: pathlib.Path,
    env: dict[str, str] | None = None,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            stdout, stderr = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            stdout, stderr = proc.communicate()
        raise subprocess.TimeoutExpired(command, timeout, output=stdout, stderr=stderr)

    completed = subprocess.CompletedProcess(command, proc.returncode, stdout, stderr)
    if completed.returncode != 0:
        raise subprocess.CalledProcessError(
            completed.returncode,
            command,
            output=completed.stdout,
            stderr=completed.stderr,
        )
    return completed


def render_workspace_artifacts(workspace: pathlib.Path, solution_paths: list[str]) -> str:
    parts = []
    for sol_path in solution_paths:
        file_path = workspace / sol_path
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            parts.append(f"--- FILE: {sol_path} ---\n{content}\n")
    return "".join(parts)


def workspace_artifacts_changed(
    source: pathlib.Path, workspace: pathlib.Path, solution_paths: list[str]
) -> bool:
    for sol_path in solution_paths:
        source_file = source / sol_path
        workspace_file = workspace / sol_path
        if not workspace_file.exists():
            continue
        if not source_file.exists():
            return True
        if workspace_file.read_text(encoding="utf-8") != source_file.read_text(encoding="utf-8"):
            return True
    return False


def workspace_artifacts_exist(workspace: pathlib.Path, solution_paths: list[str]) -> bool:
    return bool(solution_paths) and all((workspace / sol_path).is_file() for sol_path in solution_paths)


def extract_artifact_blocks(text: str, solution_paths: list[str]) -> str | None:
    marker = "--- FILE: "
    start = text.find(marker)
    if start == -1:
        return extract_write_file_tool_calls(text, solution_paths)
    candidate = text[start:].strip()
    if candidate.endswith("```"):
        candidate = candidate[:-3].strip()

    actual: set[str] = set()
    for line in candidate.splitlines():
        if line.startswith(marker) and line.endswith(" ---"):
            actual.add(line[len(marker) : -4].strip())
    expected = set(solution_paths)
    placeholder_paths = {"relative/path", "path/to/file", "owned/file"}
    actual_without_placeholders = {
        path
        for path in actual
        if path not in placeholder_paths and not path.startswith(("relative/", "path/to/"))
    }
    if actual == expected or actual_without_placeholders == expected:
        return candidate.rstrip("\r\n") + "\n"
    return extract_write_file_tool_calls(text, solution_paths)


def extract_write_file_tool_calls(text: str, solution_paths: list[str]) -> str | None:
    files: dict[str, str] = {}
    for call in re.findall(
        r"<function=write_file>(.*?)</function>",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    ):
        params = {
            name.lower(): value.strip("\r\n")
            for name, value in re.findall(
                r"<parameter=(path|content)>\s*(.*?)\s*</parameter>",
                call,
                flags=re.DOTALL | re.IGNORECASE,
            )
        }
        if "path" in params and "content" in params:
            files[params["path"].strip()] = params["content"]

    if set(files) != set(solution_paths):
        return None
    return "".join(
        f"--- FILE: {path} ---\n{files[path].rstrip()}\n" for path in solution_paths
    )


def normalize_artifact_submission(text: str, solution_paths: list[str]) -> str:
    recovered = extract_artifact_blocks(text, solution_paths)
    if recovered is not None:
        return recovered
    if len(solution_paths) != 1:
        return text

    fenced = re.findall(r"```(?:rust|rs)?\s*\n(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    for block in fenced:
        candidate = block.strip()
        if "fn " in candidate or "pub " in candidate or "use " in candidate:
            return f"--- FILE: {solution_paths[0]} ---\n{candidate.rstrip()}\n"
    return text


def run_holon_prompt_fallback(
    holon_bin: str,
    workspace: pathlib.Path,
    env: dict[str, str],
    args: argparse.Namespace,
    prompt: str,
    timeout: float | None,
) -> str:
    fallback_prompt = workspace / "bench_prompt_fallback.txt"
    fallback_prompt.write_text(prompt, encoding="utf-8")
    try:
        completed = run_process_group(
            [
                holon_bin,
                "--model",
                args.model,
                "--print",
                "--prompt-file",
                str(fallback_prompt),
            ],
            cwd=workspace,
            env=env,
            timeout=timeout,
        )
        return completed.stdout
    except subprocess.CalledProcessError as exc:
        return f"{exc.output or ''}\n{exc.stderr or ''}"
    except subprocess.TimeoutExpired as exc:
        return f"{exc.output or ''}\n{exc.stderr or ''}"


GRAPH_TOOLS = {
    "RecallMemory",
    "QueryKnowledge",
    "TraverseKnowledge",
    "VerifyConstraints",
}

GRAPH_SEMANTIC_CHECKS = {
    "graph_context_used",
    "graph_relation_used",
    "project_scoped_graph_context",
}

HOLON_CLI_MAX_AGENT_ITERATIONS = 12


def detect_called_tools(text: str) -> list[str]:
    called: set[str] = set()
    for line in text.splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            for tool in payload.get("graph_tool_calls", []):
                if tool in GRAPH_TOOLS:
                    called.add(tool)
        message = payload.get("message", {}) if isinstance(payload, dict) else {}
        for block in message.get("blocks", []):
            if (
                isinstance(block, dict)
                and block.get("type") == "tool_use"
                and block.get("name") in GRAPH_TOOLS
            ):
                called.add(block["name"])
    return sorted(called)


def read_holon_governance(snapshot_roots: list[pathlib.Path]) -> dict:
    for root in snapshot_roots:
        path = root / ".holon" / "governance.json"
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        mode = data.get("governance_mode")
        if mode not in {"governed", "ungoverned"}:
            continue
        governance: dict = {"governance_mode": mode}
        checks = data.get("governance_checks")
        if isinstance(checks, list):
            governance["governance_checks"] = checks
        elif mode == "ungoverned":
            governance["governance_checks"] = []
        chain = data.get("tao_truth_chain")
        if isinstance(chain, dict):
            governance["tao_truth_chain"] = chain
        record = data.get("acceptance_record")
        if isinstance(record, dict):
            governance["acceptance_record"] = record
        return governance
    return {}


def collect_holon_trace(
    *,
    workspace: pathlib.Path,
    home_dir: pathlib.Path,
    auto_stdout: str,
    fallback_stdout: str = "",
    snapshot_roots: list[pathlib.Path] | None = None,
) -> dict:
    roots = snapshot_roots or []
    trace_text = [auto_stdout, fallback_stdout]
    trace_files = []
    for base in [workspace / ".holon", home_dir / ".holon"]:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            rel = path.relative_to(base).as_posix()
            trace_files.append(
                {
                    "base": str(base),
                    "path": rel,
                    "bytes": len(content.encode("utf-8", errors="ignore")),
                    "tail": content[-12000:],
                }
            )
            trace_text.append(content)
    artifact_snapshots = []
    for root in roots:
        if not root.exists():
            continue
        for rel in [
            "reports/graph_recall.md",
            "reports/design_critique.md",
            "reports/implement_artifact_rejection.md",
            "reports/repair_artifact_rejection.md",
            "src/router.py",
            "src/review.py",
            "src/banner.py",
        ]:
            path = root / rel
            if not path.is_file():
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            artifact_snapshots.append(
                {
                    "root": str(root),
                    "path": rel,
                    "bytes": len(content.encode("utf-8", errors="ignore")),
                    "tail": content[-12000:],
                }
            )
    combined = "\n".join(trace_text)
    trace = {
        "called_tools": detect_called_tools(combined),
        "auto_stdout_tail": auto_stdout[-12000:],
        "fallback_stdout_tail": fallback_stdout[-12000:],
        "trace_files": trace_files,
        "artifact_snapshots": artifact_snapshots,
    }
    trace.update(read_holon_governance(roots))
    return trace


def mark_generation_path(
    metadata: dict,
    *,
    generation_path: str,
    fallback_used: bool,
    workflow_attempted: bool,
    workflow_type: str = "none",
    governance_level: str | None = None,
    prompt_stack: dict | None = None,
) -> dict:
    if governance_level is None:
        governance_level = governance_level_for_path(generation_path)
    marked = dict(metadata)
    marked.update(
        {
            "generation_path": generation_path,
            "fallback_used": fallback_used,
            "workflow_attempted": workflow_attempted,
            "workflow_type": workflow_type,
            "governance_level": governance_level,
            "prompt_stack": prompt_stack,
        }
    )
    return marked


def governance_level_for_path(generation_path: str) -> str:
    if generation_path == "holon_workflow":
        return "whitebox_native"
    if generation_path in {"holon_auto", "holon_print", "claw_cli"}:
        return "graybox_workspace"
    return "blackbox_artifact"


def should_use_graph_recall_workflow(case: dict) -> bool:
    semantic_checks = set(case.get("verifier", {}).get("semantic_checks", []))
    return bool(semantic_checks & GRAPH_SEMANTIC_CHECKS)


def graph_recall_queries_for_case(case: dict) -> list[str]:
    node_queries = [
        str(node.get("name", "")).strip()
        for node in case.get("knowledge_seed", [])
        if str(node.get("name", "")).strip()
    ]
    return node_queries + [
        f"Stored project decisions and requirements relevant to {case['id']}: {case['user_request'].strip()}",
        "Project memory that constrains the requested implementation behavior",
    ]


def write_graph_recall_workflow(
    *,
    workspace: pathlib.Path,
    case: dict,
    args: argparse.Namespace,
) -> pathlib.Path:
    solution_paths = case.get("solution_paths", [])
    verifier_commands = case.get("verifier", {}).get("commands", [])
    max_iterations = max(4, min(args.holon_max_iterations, 8))
    constraints = "\n".join(f"- {item}" for item in case["constraints"])
    allowed = "\n".join(f"- {item}" for item in case["allowed_paths"])
    forbidden = "\n".join(f"- {item}" for item in case["forbidden_paths"])
    protected = "\n".join(f"- {item}" for item in case.get("protected_paths", [])) or "- none"
    targets = "\n".join(f"- {path}" for path in solution_paths)
    workflow = {
        "name": f"HolonBench_GraphRecall_{case['id']}",
        "execution_mode": "serial",
        "states": [
            {
                "id": "recall",
                "description": "Recall project knowledge before implementation.",
                "role": "Planner",
                "model": args.model,
                "base_url_override": args.endpoint,
                "permission_mode": "read-only",
                "allowed_tools": [],
                "max_iterations": 3,
                "thinking_budget": 768,
                "max_output_tokens": 16384,
                "artifact_output_path": "reports/graph_recall.md",
                "graph_recall": {
                    "required": True,
                    "queries": graph_recall_queries_for_case(case),
                    "minimum_tool_calls": 1,
                },
                "next_states": ["implement"],
                "instructions_override": f"""Clean-context benchmark recall state.

Use the provided graph recall queries exactly when possible. Call project knowledge graph recall/search tools, then stop calling tools.
Summarize only the recalled project decision, requirement, or constraint needed by the implementer.
Include exact policy strings, warning strings, formats, or target values returned by graph tools.
If no memory is found, say MEMORY_NOT_FOUND. Do not inspect files and do not implement code.

CASE ID: {case['id']}
TASK:
{case['user_request'].strip()}
""",
            },
            {
                "id": "implement",
                "description": "Implement the benchmark task using the recalled project memory.",
                "role": "Developer",
                "model": args.model,
                "base_url_override": args.endpoint,
                "permission_mode": "read-only",
                "allowed_tools": [],
                "max_iterations": 1,
                "thinking_budget": 768,
                "max_output_tokens": 16384,
                "artifact_inputs": ["reports/graph_recall.md"],
                "context_globs": ["README.md", "src/**/*.py", "tests/**/*.py"],
                "artifact_output_paths": solution_paths,
                "next_states": ["verify"],
                "instructions_override": f"""Clean-context benchmark implementation state.

Output ONLY complete owned file artifacts in this exact format:
--- FILE: relative/path ---
complete file content

The first line of your response must be exactly:
--- FILE: {solution_paths[0] if solution_paths else 'relative/path'} ---

Write exactly these owned files and no others:
{targets}

Use the recalled project memory from the shared context section named:
--- ARTIFACT: reports/graph_recall.md ---
Treat exact policy strings, warning strings, formats, and target values in that artifact as authoritative.
If the recalled policy gives a domain concept but the source files do not define one exact input schema, implement a conservative domain predicate instead of guessing one brittle field name.
For account-safety style policies, treat settled-account evidence as any common settled marker such as `settled is true` or `account_state`, `account_status`, `status`, or `state` equal to `"settled"`; treat external integration evidence as `source`, `requestor`, `origin`, or `actor` equal to `"external_api"`; treat mutation evidence as `operation`, `action`, or `type` equal to `"mutation"` or a non-zero amount.

Do not call tools. Do not output a patch. Do not use Markdown fences. Do not include explanation outside file artifacts.

CASE ID: {case['id']}
TASK:
{case['user_request'].strip()}

CONSTRAINTS:
{constraints}

ALLOWED PATHS:
{allowed}

FORBIDDEN PATHS:
{forbidden}

PROTECTED PATHS (read-only verifier assets; do not modify):
{protected}
""",
            },
            {
                "id": "verify",
                "description": "Run deterministic benchmark verifiers.",
                "role": "Reviewer",
                "permission_mode": "danger-full-access",
                "commands": verifier_commands,
                "next_states": ["completed", "repair", "failed_exit"],
                "transitions": [
                    {
                        "condition": {
                            "type": "output_contains",
                            "value": "VERIFY_VERDICT: PASS",
                        },
                        "next_state": "completed",
                    },
                    {
                        "condition": {
                            "type": "output_contains",
                            "value": "VERIFY_VERDICT: FAIL",
                        },
                        "next_state": "repair",
                        "max_retries": 1,
                        "on_max_retries": "failed_exit",
                    },
                ],
            },
            {
                "id": "repair",
                "description": "Repair the failed artifact using verifier feedback.",
                "role": "Developer",
                "model": args.model,
                "base_url_override": args.endpoint,
                "permission_mode": "read-only",
                "allowed_tools": [],
                "max_iterations": 1,
                "thinking_budget": 768,
                "max_output_tokens": 16384,
                "artifact_inputs": ["reports/graph_recall.md"],
                "context_globs": ["README.md", "src/**/*.py", "tests/**/*.py"],
                "artifact_output_paths": solution_paths,
                "next_states": ["verify"],
                "instructions_override": f"""Clean-context benchmark repair state.

You are repairing a failed file artifact. Think internally about the verifier failure and make the smallest sufficient correction.

Output ONLY complete owned file artifacts in this exact format:
--- FILE: relative/path ---
complete file content

The first line of your response must be exactly:
--- FILE: {solution_paths[0] if solution_paths else 'relative/path'} ---

Write exactly these owned files and no others:
{targets}

Use the recalled project memory from the shared context section named:
--- ARTIFACT: reports/graph_recall.md ---
Treat exact policy strings, warning strings, formats, and target values in that artifact as authoritative.
If the recalled policy gives a domain concept but the source files do not define one exact input schema, implement a conservative domain predicate instead of guessing one brittle field name.
For account-safety style policies, treat settled-account evidence as any common settled marker such as `settled is true` or `account_state`, `account_status`, `status`, or `state` equal to `"settled"`; treat external integration evidence as `source`, `requestor`, `origin`, or `actor` equal to `"external_api"`; treat mutation evidence as `operation`, `action`, or `type` equal to `"mutation"` or a non-zero amount.

Verifier feedback from the failed attempt:
{{{{output.verify}}}}

Repair rules:
- Do not call tools.
- Do not explain the bug.
- Do not repeat the verifier output.
- Do not redesign unrelated code.
- Preserve existing passing behavior.
- If the verifier expected a warning but got an empty list, repair the predicate that decides when the warning is emitted.
- Do not repeat the same failed predicate under a different spelling; map the recalled policy to common domain fields and values already implied by the task.
- Return only the corrected complete file artifact.

CASE ID: {case['id']}
TASK:
{case['user_request'].strip()}

CONSTRAINTS:
{constraints}

ALLOWED PATHS:
{allowed}

FORBIDDEN PATHS:
{forbidden}

PROTECTED PATHS (read-only verifier assets; do not modify):
{protected}
""",
            },
            {
                "id": "completed",
                "description": "Benchmark case completed.",
                "role": "Reviewer",
                "permission_mode": "danger-full-access",
                "commands": ["true"],
                "next_states": [],
            },
            {
                "id": "failed_exit",
                "description": "Benchmark verifier failed.",
                "role": "Reviewer",
                "permission_mode": "danger-full-access",
                "commands": ["false"],
                "next_states": [],
            },
        ],
    }
    workflow_path = workspace / ".holon" / "bench_graph_recall_workflow.json"
    workflow_path.write_text(json.dumps(workflow, indent=2), encoding="utf-8")
    return workflow_path


def benchmark_context_globs_for_case(case: dict) -> list[str]:
    language = case.get("language", "")
    common = [
        "README.md",
        "pyproject.toml",
        "Cargo.toml",
        "go.mod",
        "pubspec.yaml",
    ]
    by_language = {
        "python": ["src/**/*.py", "tests/**/*.py"],
        "rust": ["src/**/*.rs", "tests/**/*.rs"],
        "go": ["**/*.go"],
        "dart": ["lib/**/*.dart", "test/**/*.dart"],
    }
    return common + by_language.get(language, ["src/**/*", "tests/**/*", "lib/**/*", "test/**/*"])


def write_artifact_workflow(
    *,
    workspace: pathlib.Path,
    case: dict,
    args: argparse.Namespace,
) -> pathlib.Path:
    solution_paths = case.get("solution_paths", [])
    constraints = "\n".join(f"- {item}" for item in case["constraints"])
    allowed = "\n".join(f"- {item}" for item in case["allowed_paths"])
    forbidden = "\n".join(f"- {item}" for item in case["forbidden_paths"])
    protected = "\n".join(f"- {item}" for item in case.get("protected_paths", [])) or "- none"
    targets = "\n".join(f"- {path}" for path in solution_paths)
    previous_artifact = ""
    previous_artifact_path = getattr(args, "previous_artifact", None)
    if previous_artifact_path:
        previous_path = pathlib.Path(previous_artifact_path)
        if previous_path.exists():
            previous_artifact = previous_path.read_text(encoding="utf-8", errors="replace")
    feedback = getattr(args, "feedback_error", None) or ""
    repair_section = ""
    if previous_artifact or feedback:
        repair_section = f"""
PREVIOUS ATTEMPT ARTIFACT:
{previous_artifact.strip()}

VERIFIER FEEDBACK:
{feedback.strip()}

Repair rules:
- Think internally about the verifier failure, then output the smallest sufficient correction.
- Preserve existing passing behavior.
- Do not repeat the same failed predicate under a different spelling.
"""

    workflow = {
        "name": f"HolonBench_Artifact_{case['id']}",
        "execution_mode": "serial",
        "states": [
            {
                "id": "implement",
                "description": "Implement one benchmark artifact task with bounded reasoning.",
                "role": "Developer",
                "model": args.model,
                "base_url_override": args.endpoint,
                "permission_mode": "read-only",
                "allowed_tools": [],
                "max_iterations": 1,
                "thinking_budget": 768,
                "max_output_tokens": 16384,
                "context_globs": benchmark_context_globs_for_case(case),
                "artifact_output_paths": solution_paths,
                "next_states": [],
                "instructions_override": f"""Clean-context benchmark implementation state.

Output ONLY complete owned file artifacts in this exact format:
--- FILE: relative/path ---
complete file content

The first line of your response must be exactly:
--- FILE: {solution_paths[0] if solution_paths else 'relative/path'} ---

Write exactly these owned files and no others:
{targets}

Do not call tools. Do not output a patch. Do not use Markdown fences. Do not include explanation outside file artifacts.

CASE ID: {case['id']}
TASK:
{case['user_request'].strip()}

CONSTRAINTS:
{constraints}

ALLOWED PATHS:
{allowed}

FORBIDDEN PATHS:
{forbidden}

PROTECTED PATHS (read-only verifier assets; do not modify):
{protected}
{repair_section}
""",
            }
        ],
    }
    if getattr(args, "plan_critique", False):
        # M1-equivalent (holon "policy in YAML/workflow units" doctrine): a plan-phase
        # design-critique state runs first using holon's official critic prompt, commits a
        # design to reports/design_critique.md, which the implement state reads via
        # artifact_inputs. Default off -> states list is byte-identical to above.
        workflow["states"][0]["artifact_inputs"] = ["reports/design_critique.md"]
        workflow["states"].insert(0, {
            "id": "design_critique",
            "description": "Plan-phase design critique before implementation.",
            "role": "Reviewer",
            "model": args.model,
            "base_url_override": args.endpoint,
            "permission_mode": "read-only",
            "allowed_tools": [],
            "max_iterations": 1,
            "thinking_budget": 768,
            "max_output_tokens": 4096,
            "artifact_output_path": "reports/design_critique.md",
            "next_states": ["implement"],
            "instructions_override": f"""You are a senior software design reviewer operating in the PLAN phase, BEFORE any code is written.
Given a programming task, do the following in one pass:
1. Enumerate the candidate internal designs / data structures.
2. For each, weigh the trade-offs explicitly — especially memory-safety, how much `unsafe` (or equivalent footguns) it requires, idiomaticity, and complexity.
3. COMMIT to the single safest viable design that still meets the requirements; prefer safe, idiomatic constructs over unsafe/raw approaches unless the task truly demands otherwise.
Output ONLY the committed design decision: the chosen data structures, safe-vs-unsafe stance, and a one-line justification. Do NOT write the implementation.

CASE ID: {case['id']}
TASK:
{case['user_request'].strip()}

CONSTRAINTS:
{constraints}

ALLOWED PATHS:
{allowed}

Produce the committed design decision now (no implementation code).""",
        })

    workflow_path = workspace / ".holon" / "bench_artifact_workflow.json"
    workflow_path.write_text(json.dumps(workflow, indent=2), encoding="utf-8")
    return workflow_path


def latest_holon_worktree(workspace: pathlib.Path) -> pathlib.Path | None:
    worktrees_dir = workspace / ".holon" / "worktrees"
    if not worktrees_dir.exists():
        return None
    candidates = [path for path in worktrees_dir.iterdir() if path.is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def run_holon_cli_driver(
    root: pathlib.Path,
    case: dict,
    args: argparse.Namespace,
    prompt: str,
    fallback_prompt: str,
) -> str:
    source = (root / case["fixture"]).resolve()
    with tempfile.TemporaryDirectory(prefix=f"holon-bench-{case['id']}-") as temp:
        workspace = pathlib.Path(temp) / source.name
        shutil.copytree(source, workspace, ignore=generation_fixture_ignore)
        ensure_git_repo(workspace)

        holon_dir = workspace / ".holon"
        holon_dir.mkdir(exist_ok=True)
        if case.get("knowledge_seed"):
            (holon_dir / "knowledge_seed.json").write_text(
                json.dumps({"nodes": case["knowledge_seed"]}, indent=2),
                encoding="utf-8",
            )
        cognitive_recall = bool(case.get("cognitive_recall", False))
        agent_max_iterations = max(
            4,
            min(args.holon_max_iterations, HOLON_CLI_MAX_AGENT_ITERATIONS),
        )
        (holon_dir / "settings.json").write_text(
            json.dumps(
                {
                    "capabilities": {
                        "maxIterations": agent_max_iterations,
                        "autoIsolate": True,
                        "cognitiveRecall": {
                            "enabled": cognitive_recall,
                            "threshold": 0.85,
                            "limit": 5,
                        },
                    }
                }
            ),
            encoding="utf-8",
        )
        exclude_file = workspace / ".git" / "info" / "exclude"
        with exclude_file.open("a", encoding="utf-8") as handle:
            handle.write("\n.holon/\nbench_prompt.txt\n")

        prompt_file = workspace / "bench_prompt.txt"
        prompt_file.write_text(prompt, encoding="utf-8")

        env = os.environ.copy()
        home_dir = pathlib.Path(temp) / "home"
        home_dir.mkdir(parents=True, exist_ok=True)
        env["HOME"] = str(home_dir)
        env["LLAMACPP_BASE_URL"] = args.endpoint
        env["LLAMACPP_API_KEY"] = "dummy"
        env["OLLAMA_BASE_URL"] = args.endpoint
        env["OPENAI_BASE_URL"] = args.endpoint
        env["KLAW_MODEL"] = args.model
        env["OPENAI_API_KEY"] = "dummy"
        # Pin the local OpenAI-compatible endpoint and remove any Anthropic key:
        # holon's provider detection falls back to Anthropic for model names it does
        # not recognise as local (e.g. "qwythos" has no qwen/gemma substring), which
        # 404s. Routing every holon-cli run at the launched server avoids that.
        env.pop("ANTHROPIC_API_KEY", None)
        env.pop("ANTHROPIC_BASE_URL", None)

        # HOME is set to a fresh temp dir to isolate holon's .holon state between runs.
        # Preserve RUSTUP_HOME/CARGO_HOME so rustup can still find its toolchain config
        # (stored in the real HOME), preventing preflight from wrongly marking rustc as
        # unavailable and falling back to --print mode (which has no graph tools).
        real_home = os.environ.get("HOME", str(pathlib.Path.home()))
        env.setdefault("RUSTUP_HOME", os.path.join(real_home, ".rustup"))
        env.setdefault("CARGO_HOME", os.path.join(real_home, ".cargo"))

        holon_bin = os.environ.get("HOLON_BIN", "/home/taichi/Migration/holon/target/debug/holon")
        if not pathlib.Path(holon_bin).exists():
            raise SystemExit(f"compiled holon binary not found at: {holon_bin}. Run cargo build first.")


        session_id = f"session-{case['id']}"
        auto_stdout = ""
        use_graph_workflow = should_use_graph_recall_workflow(case)
        use_artifact_workflow = args.protocol == "artifact"
        workflow_attempted = False
        if not args.holon_skip_auto:
            try:
                if use_graph_workflow:
                    workflow_attempted = True
                    workflow_path = write_graph_recall_workflow(
                        workspace=workspace,
                        case=case,
                        args=args,
                    )
                    completed = run_process_group(
                        [
                            holon_bin,
                            "--workflow",
                            str(workflow_path),
                            case["user_request"].strip(),
                        ],
                        cwd=workspace,
                        env=env,
                        timeout=args.holon_timeout_seconds,
                    )
                elif use_artifact_workflow:
                    workflow_attempted = True
                    workflow_path = write_artifact_workflow(
                        workspace=workspace,
                        case=case,
                        args=args,
                    )
                    completed = run_process_group(
                        [
                            holon_bin,
                            "--workflow",
                            str(workflow_path),
                            case["user_request"].strip(),
                        ],
                        cwd=workspace,
                        env=env,
                        timeout=args.holon_auto_timeout_seconds,
                    )
                else:
                    completed = run_process_group(
                        [
                            holon_bin,
                            "--model",
                            args.model,
                            "--auto",
                            "--max-turns",
                            "1",
                            "--dangerously-skip-permissions",
                            "--allowed-tools",
                            "read_file,write_file,edit_file,bash,RecallMemory,QueryKnowledge,TraverseKnowledge,VerifyConstraints,ContextStatus",
                            "--prompt-file",
                            str(prompt_file),
                            "--session-id",
                            session_id,
                        ],
                        cwd=workspace,
                        env=env,
                        timeout=args.holon_auto_timeout_seconds,
                    )
                auto_stdout = completed.stdout
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as exc:
                output = getattr(exc, "output", None)
                if isinstance(output, str):
                    auto_stdout = output
                stderr = getattr(exc, "stderr", None)
                if isinstance(stderr, str):
                    auto_stdout += "\n" + stderr

        worktree_dir = (
            latest_holon_worktree(workspace)
            if use_graph_workflow or use_artifact_workflow
            else workspace / ".holon" / "worktrees" / session_id
        )
        if worktree_dir is None:
            worktree_dir = workspace
        if not worktree_dir.exists():
            worktree_dir = workspace
        metadata = collect_holon_trace(
            workspace=workspace,
            home_dir=home_dir,
            auto_stdout=auto_stdout,
            snapshot_roots=[workspace, worktree_dir],
        )

        workflow_type = (
            "graph_recall"
            if use_graph_workflow and workflow_attempted
            else "artifact"
            if use_artifact_workflow and workflow_attempted
            else "none"
        )
        primary_generation_path = "holon_workflow" if workflow_attempted else "holon_auto"

        if args.protocol == "patch":
            diff = subprocess.run(
                ["git", "diff"],
                cwd=worktree_dir,
                capture_output=True,
                text=True,
                check=True,
            ).stdout
            return diff, mark_generation_path(
                metadata,
                generation_path=primary_generation_path,
                fallback_used=False,
                workflow_attempted=workflow_attempted,
                workflow_type=workflow_type,
            )

        solution_paths = case.get("solution_paths", [])
        artifact_roots = [workspace, worktree_dir] if workflow_attempted else [worktree_dir]
        for artifact_root in artifact_roots:
            if workspace_artifacts_changed(source, artifact_root, solution_paths):
                return render_workspace_artifacts(artifact_root, solution_paths), mark_generation_path(
                    metadata,
                    generation_path=primary_generation_path,
                    fallback_used=False,
                    workflow_attempted=workflow_attempted,
                    workflow_type=workflow_type,
                )
        if use_graph_workflow and workflow_attempted:
            for artifact_root in artifact_roots:
                if workspace_artifacts_exist(artifact_root, solution_paths):
                    return render_workspace_artifacts(artifact_root, solution_paths), mark_generation_path(
                        metadata,
                        generation_path=primary_generation_path,
                        fallback_used=False,
                        workflow_attempted=workflow_attempted,
                        workflow_type=workflow_type,
                    )

        recovered = extract_artifact_blocks(auto_stdout, solution_paths)
        if recovered is not None:
            return recovered, mark_generation_path(
                metadata,
                generation_path=primary_generation_path,
                fallback_used=False,
                workflow_attempted=workflow_attempted,
                workflow_type=workflow_type,
            )

        if workflow_attempted:
            return auto_stdout, mark_generation_path(
                metadata,
                generation_path="holon_workflow",
                fallback_used=False,
                workflow_attempted=True,
                workflow_type=workflow_type,
            )

        fallback_stdout = run_holon_prompt_fallback(
            holon_bin,
            workspace,
            env,
            args,
            fallback_prompt,
            timeout=min(args.holon_timeout_seconds, args.holon_auto_timeout_seconds),
        )
        metadata = collect_holon_trace(
            workspace=workspace,
            home_dir=home_dir,
            auto_stdout=auto_stdout,
            fallback_stdout=fallback_stdout,
            snapshot_roots=[workspace, worktree_dir],
        )
        recovered = extract_artifact_blocks(fallback_stdout, solution_paths)
        if recovered is not None:
            return recovered, mark_generation_path(
                metadata,
                generation_path="holon_print",
                fallback_used=True,
                workflow_attempted=False,
            )
        direct_fallback = request_patch(
            args.endpoint,
            args.model,
            fallback_prompt,
            max_output_tokens=args.max_output_tokens,
            generation_timeout_seconds=args.generation_timeout_seconds,
            temperature=args.temperature,
            top_p=args.top_p,
            min_p=args.min_p,
            reasoning_budget=args.reasoning_budget,
        )
        recovered = extract_artifact_blocks(direct_fallback, solution_paths)
        if recovered is not None:
            return recovered, mark_generation_path(
                metadata,
                generation_path="direct",
                fallback_used=True,
                workflow_attempted=False,
            )
        return direct_fallback, mark_generation_path(
            metadata,
            generation_path="direct",
            fallback_used=True,
            workflow_attempted=False,
        )


def run_claw_cli_driver(
    root: pathlib.Path,
    case: dict,
    args: argparse.Namespace,
    prompt: str,
    fallback_prompt: str,
) -> str:
    source = (root / case["fixture"]).resolve()
    with tempfile.TemporaryDirectory(prefix=f"holon-bench-{case['id']}-") as temp:
        workspace = pathlib.Path(temp) / source.name
        ignore = shutil.ignore_patterns(".git", ".claw", ".holon", "__pycache__", "target", "bench_prompt.txt")
        shutil.copytree(source, workspace, ignore=ignore)
        ensure_git_repo(workspace)

        exclude_file = workspace / ".git" / "info" / "exclude"
        with exclude_file.open("a", encoding="utf-8") as handle:
            handle.write("\n.claw/\nbench_prompt.txt\n")

        prompt_file = workspace / "bench_prompt.txt"
        prompt_file.write_text(prompt, encoding="utf-8")

        env = os.environ.copy()
        env["DASHSCOPE_BASE_URL"] = args.endpoint
        env["DASHSCOPE_API_KEY"] = "dummy"
        env["OPENAI_BASE_URL"] = args.endpoint
        env["OPENAI_API_KEY"] = "dummy"
        env["ANTHROPIC_BASE_URL"] = args.endpoint
        env["ANTHROPIC_API_KEY"] = "dummy"

        claw_bin = os.environ.get("CLAW_BIN", "/home/taichi/Migration/claw-code/rust/target/debug/claw")
        if not pathlib.Path(claw_bin).exists():
            raise SystemExit(f"compiled claw binary not found at: {claw_bin}. Run cargo build first.")

        auto_stdout = ""
        if not args.holon_skip_auto:
            try:
                completed = run_process_group(
                    [
                        claw_bin,
                        "prompt",
                        prompt,
                        "--model",
                        args.model,
                        "--dangerously-skip-permissions",
                        "--allowed-tools",
                        "read_file,write_file,edit_file,bash",
                    ],
                    cwd=workspace,
                    env=env,
                    timeout=args.holon_auto_timeout_seconds,
                )
                auto_stdout = completed.stdout
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as exc:
                output = getattr(exc, "output", None)
                if isinstance(output, str):
                    auto_stdout = output

        if args.protocol == "patch":
            diff = subprocess.run(
                ["git", "diff"],
                cwd=workspace,
                capture_output=True,
                text=True,
                check=True,
            ).stdout
            return diff, mark_generation_path({
                "called_tools": detect_called_tools(auto_stdout),
                "auto_stdout_tail": auto_stdout[-12000:],
            }, generation_path="claw_cli", fallback_used=False, workflow_attempted=False)

        solution_paths = case.get("solution_paths", [])
        if workspace_artifacts_changed(source, workspace, solution_paths):
            return render_workspace_artifacts(workspace, solution_paths), mark_generation_path({
                "called_tools": detect_called_tools(auto_stdout),
                "auto_stdout_tail": auto_stdout[-12000:],
            }, generation_path="claw_cli", fallback_used=False, workflow_attempted=False)

        recovered = extract_artifact_blocks(auto_stdout, solution_paths)
        if recovered is not None:
            return recovered, mark_generation_path({
                "called_tools": detect_called_tools(auto_stdout),
                "auto_stdout_tail": auto_stdout[-12000:],
            }, generation_path="claw_cli", fallback_used=False, workflow_attempted=False)

        direct_fallback = request_patch(
            args.endpoint,
            args.model,
            fallback_prompt,
            max_output_tokens=args.max_output_tokens,
            generation_timeout_seconds=args.generation_timeout_seconds,
            temperature=args.temperature,
            top_p=args.top_p,
            min_p=args.min_p,
            reasoning_budget=args.reasoning_budget,
        )
        recovered = extract_artifact_blocks(direct_fallback, solution_paths)
        if recovered is not None:
            return recovered, mark_generation_path({
                "called_tools": detect_called_tools(auto_stdout),
                "auto_stdout_tail": auto_stdout[-12000:],
            }, generation_path="direct", fallback_used=True, workflow_attempted=False)
        return direct_fallback, mark_generation_path({
            "called_tools": detect_called_tools(auto_stdout),
            "auto_stdout_tail": auto_stdout[-12000:],
        }, generation_path="direct", fallback_used=True, workflow_attempted=False)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_id")
    parser.add_argument("--model", required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--bench-root", default=".")
    parser.add_argument("--out")
    parser.add_argument("--protocol", choices=["patch", "artifact"], default="patch")
    parser.add_argument("--driver", choices=["direct", "holon-cli", "claw-cli"], default="direct")
    parser.add_argument("--max-context-chars", type=int, default=40000)
    # Holon-aligned generation controls. These mirror Holon workflow fields so the
    # direct driver shares one vocabulary with Holon instead of an ad-hoc one.
    parser.add_argument(
        "--max-output-tokens",
        "--generation-max-tokens",
        dest="max_output_tokens",
        type=int,
        default=None,
        help="Holon workflow field max_output_tokens. Sent as OpenAI-compatible "
        "max_tokens on direct requests. --generation-max-tokens is a deprecated alias.",
    )
    parser.add_argument(
        "--thinking-budget",
        type=int,
        default=None,
        help="Holon workflow field thinking_budget. Recorded in generation metadata; "
        "not sent as a request field unless the endpoint convention already supports one.",
    )
    parser.add_argument(
        "--generation-timeout-seconds",
        type=float,
        default=600.0,
        help="Per-request generation timeout in seconds for the direct driver.",
    )
    # Sampling-profile controls for the direct driver. Defaults reproduce the
    # conservative deterministic-baseline profile.
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="Sampling temperature sent on direct requests. 0 = greedy.",
    )
    parser.add_argument(
        "--top-p",
        type=float,
        default=0.9,
        help="Nucleus sampling top_p sent on direct requests.",
    )
    parser.add_argument(
        "--min-p",
        type=float,
        default=None,
        help="min_p sent on direct requests only when provided.",
    )
    parser.add_argument(
        "--reasoning-budget",
        type=int,
        default=None,
        help="Server-side reasoning-token budget (llama.cpp `reasoning_budget` "
        "extension), mirroring the field Holon's openai_compat provider sends. Sent "
        "on direct requests only when provided; default behavior is unchanged.",
    )
    parser.add_argument(
        "--stream-early-stop",
        action="store_true",
        help="Direct driver only: stream the generation and cut it off content-side "
        "when rumination is detected (a duplicate `--- FILE:` marker for a single-owned "
        "file, or a substantial line repeating --repeat-threshold times). Default off "
        "uses the blocking single-shot request.",
    )
    parser.add_argument(
        "--repeat-threshold",
        type=int,
        default=4,
        help="Repetition count that trips the streaming early-stop loop detector.",
    )
    parser.add_argument("--holon-max-iterations", type=int, default=100)
    parser.add_argument("--holon-timeout-seconds", type=float, default=540.0)
    parser.add_argument("--holon-auto-timeout-seconds", type=float, default=75.0)
    parser.add_argument("--holon-skip-auto", action="store_true")
    parser.add_argument("--previous-artifact")
    parser.add_argument("--feedback-error")
    parser.add_argument(
        "--plan-critique",
        action="store_true",
        help="Prepend a plan-phase design-critique state (M1) to the artifact workflow: "
        "the model commits a design to reports/design_critique.md, which the implement "
        "state then reads. Default off keeps the workflow byte-identical.",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()
    if any(arg == "--generation-max-tokens" or arg.startswith("--generation-max-tokens=") for arg in sys.argv):
        print(
            "warning: --generation-max-tokens is deprecated; use --max-output-tokens",
            file=sys.stderr,
        )

    root = bench_root(args.bench_root)
    case = find_case(root, args.case_id)
    files = fixture_context(root, case["fixture"], args.max_context_chars)
    prompt = (
        build_holon_cli_prompt(case, files, args.protocol)
        if args.driver in ["holon-cli", "claw-cli"]
        else build_prompt(case, files, args.protocol)
    )
    prompt = append_repair_feedback(prompt, args.previous_artifact, args.feedback_error)
    fallback_prompt = append_repair_feedback(
        build_prompt(case, files, args.protocol), args.previous_artifact, args.feedback_error
    )

    if args.driver == "claw-cli":
        patch, metadata = run_claw_cli_driver(root, case, args, prompt, fallback_prompt)
    elif args.driver == "holon-cli":
        patch, metadata = run_holon_cli_driver(root, case, args, prompt, fallback_prompt)
    else:
        generation_telemetry: dict = {}
        if args.stream_early_stop:
            patch = stream_request_patch(
                args.endpoint,
                args.model,
                prompt,
                solution_paths=case.get("solution_paths", []),
                max_output_tokens=args.max_output_tokens,
                generation_timeout_seconds=args.generation_timeout_seconds,
                temperature=args.temperature,
                top_p=args.top_p,
                min_p=args.min_p,
                reasoning_budget=args.reasoning_budget,
                repeat_threshold=args.repeat_threshold,
                telemetry=generation_telemetry,
            )
        else:
            patch = request_patch(
                args.endpoint,
                args.model,
                prompt,
                max_output_tokens=args.max_output_tokens,
                generation_timeout_seconds=args.generation_timeout_seconds,
                temperature=args.temperature,
                top_p=args.top_p,
                min_p=args.min_p,
                reasoning_budget=args.reasoning_budget,
                telemetry=generation_telemetry,
            )
        metadata = mark_generation_path(
            {
                "called_tools": [],
                "thinking_budget": args.thinking_budget,
                **generation_telemetry,
            },
            generation_path="direct",
            fallback_used=False,
            workflow_attempted=False,
        )
    if args.protocol == "artifact":
        patch = normalize_artifact_submission(patch, case.get("solution_paths", []))
    suffix = "patch.diff" if args.protocol == "patch" else "artifact.txt"
    out = pathlib.Path(args.out).resolve() if args.out else root / "reports" / f"{args.model}_{args.protocol}_{args.case_id}_{suffix}"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(patch.rstrip("\r\n") + "\n", encoding="utf-8")
    meta_out = out.with_suffix(out.suffix + ".meta.json")
    meta_out.write_text(
        json.dumps(
            {
                "case_id": case["id"],
                "model": args.model,
                "driver": args.driver,
                "protocol": args.protocol,
                **metadata,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
