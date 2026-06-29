#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import pathlib
import signal
import shutil
import subprocess
import sys
import time

from common import bench_root, load_cases, write_json


def run(args: list[str], allowed_returncodes: set[int] | None = None) -> None:
    completed = subprocess.run(args, check=False)
    allowed = allowed_returncodes or {0}
    if completed.returncode not in allowed:
        raise SystemExit(completed.returncode)


def _has_valid_score(score_path: pathlib.Path) -> bool:
    """True if a prior score json exists and looks complete (used by --resume).

    A score is complete when it parses and carries the gate summary score_case.py
    emits (``hard_pass`` plus a non-empty ``role_signals``). Partial/garbled files
    are treated as missing so the case re-runs."""
    try:
        data = json.loads(score_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(data, dict) and "hard_pass" in data and bool(data.get("role_signals"))


def run_capture_process_group(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
    proc = subprocess.Popen(
        args,
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
        raise subprocess.TimeoutExpired(args, timeout, output=stdout, stderr=stderr)
    return subprocess.CompletedProcess(args, proc.returncode, stdout, stderr)


def build_generation_command(
    runners: pathlib.Path,
    case_id: str,
    args: argparse.Namespace,
    *,
    root: pathlib.Path,
    patch_path: pathlib.Path,
    previous_artifact: pathlib.Path | None = None,
    feedback_error: str | None = None,
) -> list[str]:
    command = [
        sys.executable,
        str(runners / "run_model_case.py"),
        case_id,
        "--model",
        args.model,
        "--endpoint",
        args.endpoint,
        "--bench-root",
        str(root),
        "--out",
        str(patch_path),
        "--protocol",
        args.protocol,
        "--driver",
        args.driver,
        "--generation-timeout-seconds",
        str(args.generation_timeout_seconds),
        "--temperature",
        str(args.temperature),
        "--top-p",
        str(args.top_p),
        "--holon-max-iterations",
        str(args.holon_max_iterations),
        "--holon-timeout-seconds",
        str(max(1.0, args.generation_timeout_seconds - 10.0)),
        "--holon-auto-timeout-seconds",
        str(args.holon_auto_timeout_seconds),
    ]
    if args.min_p is not None:
        command += ["--min-p", str(args.min_p)]
    if args.reasoning_budget is not None:
        command += ["--reasoning-budget", str(args.reasoning_budget)]
    if getattr(args, "stream_early_stop", False):
        command += ["--stream-early-stop", "--repeat-threshold", str(args.repeat_threshold)]
    if args.max_output_tokens is not None:
        command += ["--max-output-tokens", str(args.max_output_tokens)]
    if args.thinking_budget is not None:
        command += ["--thinking-budget", str(args.thinking_budget)]
    if previous_artifact is not None:
        command += ["--previous-artifact", str(previous_artifact)]
    if feedback_error is not None:
        command += ["--feedback-error", feedback_error]
    return command


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("track")
    parser.add_argument("--model", required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--protocol", choices=["patch", "artifact"], default="patch")
    parser.add_argument("--driver", choices=["direct", "holon-cli", "claw-cli"], default="direct")
    parser.add_argument("--bench-root", default=".")
    parser.add_argument("--work-root", default="/tmp/holon-bench-track")
    parser.add_argument("--generation-timeout-seconds", type=float, default=90.0)
    # Holon-aligned generation controls forwarded to run_model_case.py.
    parser.add_argument(
        "--max-output-tokens",
        "--generation-max-tokens",
        dest="max_output_tokens",
        type=int,
        default=None,
        help="Holon workflow field max_output_tokens, forwarded to the direct driver "
        "as max_tokens. --generation-max-tokens is a deprecated alias.",
    )
    parser.add_argument(
        "--thinking-budget",
        type=int,
        default=None,
        help="Holon workflow field thinking_budget, forwarded to run_model_case.py.",
    )
    # Sampling-profile controls forwarded to run_model_case.py.
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--top-p", type=float, default=0.9)
    parser.add_argument("--min-p", type=float, default=None)
    parser.add_argument("--reasoning-budget", type=int, default=None)
    parser.add_argument("--stream-early-stop", action="store_true")
    parser.add_argument("--repeat-threshold", type=int, default=4)
    parser.add_argument("--holon-max-iterations", type=int, default=100)
    parser.add_argument("--holon-auto-timeout-seconds", type=float, default=75.0)
    parser.add_argument(
        "--repair-attempts",
        "--repair-budget",
        dest="repair_attempts",
        type=int,
        default=0,
        help="Maximum verifier-feedback repair attempts. --repair-budget is deprecated.",
    )
    parser.add_argument(
        "--case-ids",
        default="",
        help="Comma-separated case ids to run. Defaults to every case in the track.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip cases that already have a valid score json (opt-in; default behaviour "
        "re-runs every case). Lets a long multi-model sweep survive interruption.",
    )
    args = parser.parse_args()
    if any(arg == "--repair-budget" or arg.startswith("--repair-budget=") for arg in sys.argv):
        print(
            "warning: --repair-budget is deprecated; use --repair-attempts",
            file=sys.stderr,
        )
    if any(arg == "--generation-max-tokens" or arg.startswith("--generation-max-tokens=") for arg in sys.argv):
        print(
            "warning: --generation-max-tokens is deprecated; use --max-output-tokens",
            file=sys.stderr,
        )

    root = bench_root(args.bench_root)
    runners = root / "runners"
    cases = [case for case in load_cases(root) if case["track"] == args.track]
    selected_case_ids = {case_id.strip() for case_id in args.case_ids.split(",") if case_id.strip()}
    if selected_case_ids:
        cases = [case for case in cases if case["id"] in selected_case_ids]
    if not cases:
        raise SystemExit(f"no cases for track: {args.track}")

    score_paths: list[pathlib.Path] = []
    for case in cases:
        case_id = case["id"]
        suffix = "patch.diff" if args.protocol == "patch" else "artifact.txt"
        run_prefix = f"{args.model}_{args.driver}_{args.protocol}_{case_id}"
        patch_path = root / "reports" / f"{run_prefix}_{suffix}"
        result_path = root / "reports" / f"{run_prefix}_result.json"
        score_path = root / "reports" / f"{run_prefix}_score.json"
        if args.resume and _has_valid_score(score_path):
            print(f"[{case_id}] resume: existing score found, skipping")
            score_paths.append(score_path)
            continue
        work_root = pathlib.Path(args.work_root) / case_id
        repair_seed_artifact = case.get("repair_seed_artifact")
        if repair_seed_artifact:
            if args.protocol != "artifact":
                raise SystemExit("repair_seed_artifact cases require --protocol artifact")
            patch_path.parent.mkdir(parents=True, exist_ok=True)
            patch_path.write_text(render_seed_artifact(repair_seed_artifact), encoding="utf-8")
        else:
            generation_command = build_generation_command(
                runners,
                case_id,
                args,
                root=root,
                patch_path=patch_path,
            )
            started = time.monotonic()
            try:
                generated = run_capture_process_group(
                    generation_command,
                    args.generation_timeout_seconds,
                )
            except subprocess.TimeoutExpired as exc:
                write_generation_failure(
                    result_path,
                    case,
                    args.model,
                    args.protocol,
                    args.driver,
                    "generation_timeout",
                    time.monotonic() - started,
                    (exc.stderr or "") if isinstance(exc.stderr, str) else "",
                )
                run_score(runners, result_path, root, score_path)
                score_paths.append(score_path)
                continue
            if generated.returncode != 0:
                write_generation_failure(
                    result_path,
                    case,
                    args.model,
                    args.protocol,
                    args.driver,
                    "generation_failed",
                    time.monotonic() - started,
                    generated.stderr,
                )
                run_score(runners, result_path, root, score_path)
                score_paths.append(score_path)
                continue
        # First-pass verification
        run(
            [
                sys.executable,
                str(runners / "run_case.py"),
                case_id,
                "--model",
                args.model,
                "--patch-file" if args.protocol == "patch" else "--artifact-file",
                str(patch_path),
                "--bench-root",
                str(root),
                "--work-root",
                str(work_root),
                "--out",
                str(result_path.relative_to(root)),
            ],
            allowed_returncodes={0, 1},
        )
        annotate_result(result_path, driver=args.driver, attempt_count=1, repair_used=False)
        if repair_seed_artifact:
            annotate_repair_seed(result_path)

        res = json.loads(result_path.read_text(encoding="utf-8"))
        first_pass = all(res.get("hard_gates", {}).values())
        first_failure_tags = list(res.get("failure_tags", []))
        for repair_index in range(1, args.repair_attempts + 1):
            hard_gates = res.get("hard_gates", {})
            if all(hard_gates.values()):
                break
            attempt_number = repair_index + 1
            previous_result_path = root / "reports" / f"{run_prefix}_attempt{repair_index}_result.json"
            previous_patch_path = root / "reports" / f"{run_prefix}_attempt{repair_index}_{suffix}"
            shutil.copy2(result_path, previous_result_path)
            shutil.copy2(patch_path, previous_patch_path)

            feedback_error = build_feedback_error(case, res)
            print(f"[{case_id}] Repair loop triggered. Failed gates: {failed_gates(hard_gates)}")
            print(f"[{case_id}] Repair attempt {attempt_number}: re-generating with feedback (len={len(feedback_error)})...")
            repair_command = build_generation_command(
                runners,
                case_id,
                args,
                root=root,
                patch_path=patch_path,
                previous_artifact=previous_patch_path,
                feedback_error=feedback_error,
            )
            shutil.rmtree(work_root, ignore_errors=True)
            try:
                generated_repair = run_capture_process_group(
                    repair_command,
                    args.generation_timeout_seconds,
                )
            except subprocess.TimeoutExpired as exc:
                    annotate_result(
                        result_path,
                        driver=args.driver,
                        attempt_count=attempt_number,
                        repair_used=True,
                        first_result=previous_result_path.relative_to(root).as_posix(),
                        repair_error=f"repair generation timed out: {exc}",
                    )
                    res = json.loads(result_path.read_text(encoding="utf-8"))
                    continue
            else:
                if generated_repair.returncode != 0:
                    annotate_result(
                        result_path,
                        driver=args.driver,
                        attempt_count=attempt_number,
                        repair_used=True,
                        first_result=previous_result_path.relative_to(root).as_posix(),
                        repair_error=generated_repair.stderr[-4000:],
                    )
                    res = json.loads(result_path.read_text(encoding="utf-8"))
                    continue
                else:
                    print(f"[{case_id}] Repair attempt {attempt_number} generated successfully. Re-running verification...")
                    shutil.rmtree(work_root, ignore_errors=True)
                    run(
                        [
                            sys.executable,
                            str(runners / "run_case.py"),
                            case_id,
                            "--model",
                            args.model,
                            "--patch-file" if args.protocol == "patch" else "--artifact-file",
                            str(patch_path),
                            "--bench-root",
                            str(root),
                            "--work-root",
                            str(work_root),
                            "--out",
                            str(result_path.relative_to(root)),
                        ],
                        allowed_returncodes={0, 1},
                    )
                    preserve_better_previous_attempt(
                        result_path=result_path,
                        artifact_path=patch_path,
                        previous_result_path=previous_result_path,
                        previous_artifact_path=previous_patch_path,
                        attempt_number=attempt_number,
                    )
                    annotate_result(
                        result_path,
                        driver=args.driver,
                        attempt_count=attempt_number,
                        repair_used=True,
                        first_result=previous_result_path.relative_to(root).as_posix(),
                    )
                    res = json.loads(result_path.read_text(encoding="utf-8"))

        annotate_repair_summary(
            result_path,
            first_pass=first_pass,
            first_failure_tags=first_failure_tags,
            max_repair_attempts=args.repair_attempts,
        )
        run_score(runners, result_path, root, score_path)
        score_paths.append(score_path)

    run(
        [
            sys.executable,
            str(runners / "report.py"),
            *(str(path) for path in score_paths),
            "--bench-root",
            str(root),
        ]
    )
    return 0


def run_score(
    runners: pathlib.Path, result_path: pathlib.Path, root: pathlib.Path, score_path: pathlib.Path
) -> None:
    run(
        [
            sys.executable,
            str(runners / "score_case.py"),
            str(result_path),
            "--bench-root",
            str(root),
            "--out",
            str(score_path.relative_to(root)),
        ]
    )


def render_seed_artifact(files: dict[str, str]) -> str:
    parts = []
    for path, content in files.items():
        parts.append(f"--- FILE: {path} ---\n{content.rstrip()}\n")
    return "\n".join(parts)


def annotate_result(
    result_path: pathlib.Path,
    *,
    driver: str,
    attempt_count: int,
    repair_used: bool,
    first_result: str | None = None,
    repair_error: str | None = None,
) -> None:
    result = json.loads(result_path.read_text(encoding="utf-8"))
    result["driver"] = driver
    result["attempt_count"] = attempt_count
    result["repair_used"] = repair_used
    if first_result:
        result["first_result"] = first_result
    if repair_error:
        result["repair_error"] = repair_error
        if "repair_failed" not in result.get("failure_tags", []):
            result.setdefault("failure_tags", []).append("repair_failed")
    write_json(result_path, result)


def preserve_better_previous_attempt(
    *,
    result_path: pathlib.Path,
    artifact_path: pathlib.Path,
    previous_result_path: pathlib.Path,
    previous_artifact_path: pathlib.Path,
    attempt_number: int,
) -> bool:
    current = json.loads(result_path.read_text(encoding="utf-8"))
    previous = json.loads(previous_result_path.read_text(encoding="utf-8"))
    current_score = sum(bool(value) for value in current.get("hard_gates", {}).values())
    previous_score = sum(bool(value) for value in previous.get("hard_gates", {}).values())
    if current_score >= previous_score:
        return False

    rejected_result_path = result_path.with_name(
        result_path.name.replace("_result.json", f"_attempt{attempt_number}_rejected_result.json")
    )
    rejected_artifact_path = artifact_path.with_name(
        artifact_path.name.replace(
            artifact_path.suffix,
            f"_attempt{attempt_number}_rejected{artifact_path.suffix}",
        )
    )
    shutil.copy2(result_path, rejected_result_path)
    shutil.copy2(artifact_path, rejected_artifact_path)
    shutil.copy2(previous_result_path, result_path)
    shutil.copy2(previous_artifact_path, artifact_path)

    restored = json.loads(result_path.read_text(encoding="utf-8"))
    restored["repair_reverted"] = True
    restored["rejected_repair_result"] = rejected_result_path.name
    restored["rejected_repair_artifact"] = rejected_artifact_path.name
    restored["rejected_repair_failure_tags"] = current.get("failure_tags", [])
    restored["rejected_repair_hard_gates"] = current.get("hard_gates", {})
    write_json(result_path, restored)
    return True


def annotate_repair_seed(result_path: pathlib.Path) -> None:
    result = json.loads(result_path.read_text(encoding="utf-8"))
    result["repair_seeded"] = True
    result["initial_attempt_source"] = "repair_seed_artifact"
    write_json(result_path, result)


def annotate_repair_summary(
    result_path: pathlib.Path,
    *,
    first_pass: bool,
    first_failure_tags: list[str],
    max_repair_attempts: int,
) -> None:
    result = json.loads(result_path.read_text(encoding="utf-8"))
    attempt_count = int(result.get("attempt_count", 1) or 1)
    repair_used = bool(result.get("repair_used", False))
    final_pass = all(result.get("hard_gates", {}).values())
    repair_attempts_used = max(0, attempt_count - 1) if repair_used else 0
    result["first_pass"] = first_pass
    result["final_pass"] = final_pass
    result["repaired_pass"] = final_pass and not first_pass
    result["repair_attempts_used"] = repair_attempts_used
    result["max_repair_attempts"] = max_repair_attempts
    result["max_repair_exhausted"] = (
        (not final_pass)
        and max_repair_attempts > 0
        and repair_attempts_used >= max_repair_attempts
    )
    result["first_failure_tags"] = first_failure_tags
    result["final_failure_tags"] = result.get("failure_tags", [])
    write_json(result_path, result)


def failed_gates(hard_gates: dict) -> dict:
    return {key: value for key, value in hard_gates.items() if not value}


def build_feedback_error(case: dict, result: dict) -> str:
    hard_gates = result.get("hard_gates", {})
    if not hard_gates.get("patch_applies") or not hard_gates.get("schema_valid"):
        sub_stderr = result.get("submission", {}).get("stderr", "") or ""
        sub_stdout = result.get("submission", {}).get("stdout", "") or ""
        return f"Artifact/patch application failed.\nStderr: {sub_stderr}\nStdout: {sub_stdout}"

    failed_cmds = []
    # Only the public verifier may expose command text, stdout, and stderr.
    # Hidden and mutation verifiers are oracles: a repair attempt may learn that
    # they failed, but never their command, output, assertions, or expected
    # values. Leaking that detail would let a repair overfit to the hidden gate.
    for cmd in result.get("commands", []) or []:
        if cmd.get("exit_code") != 0 or cmd.get("timed_out"):
            failed_cmds.append(
                "Public Verifier failed.\n"
                f"Command: {cmd.get('command')}\n"
                f"Exit Code: {cmd.get('exit_code')}\n"
                f"Timed Out: {bool(cmd.get('timed_out'))}\n"
                f"Stdout:\n{cmd.get('stdout', '')}\n"
                f"Stderr:\n{cmd.get('stderr', '')}"
            )
    if any(
        cmd.get("exit_code") != 0 or cmd.get("timed_out")
        for cmd in result.get("hidden_commands", []) or []
    ):
        failed_cmds.append("Hidden verifier failed. Details withheld.")
    if any(
        cmd.get("exit_code") != 0 or cmd.get("timed_out")
        for cmd in result.get("mutation_commands", []) or []
    ):
        failed_cmds.append("Mutation verifier failed. Details withheld.")
    for check in result.get("semantic_checks", []) or []:
        if isinstance(check, dict) and not check.get("passed", True):
            # Expose only the check name; free-form diagnostic/detail/message
            # bodies may carry oracle specifics.
            failed_cmds.append(
                "Semantic verifier failed.\n"
                f"Check: {check.get('name', check.get('check', 'unknown'))}\n"
                "Diagnostic: withheld."
            )
    if failed_cmds:
        feedback = "\n\n".join(failed_cmds)
    else:
        feedback = "Some checks failed, but no specific verifier command failed."

    if case.get("task_type") == "process_wrapper_port":
        feedback += (
            "\n\nRUST STD PROCESS CONSTRAINTS FOR THIS TASK:\n"
            "- Do not use Child::wait_timeout; it is not in std.\n"
            "- Do not use std::process::Output::default or unwrap_or_default on Output.\n"
            "- Do not use std::thread::spawn, channels, or recv_timeout for waiting on the child process; they move ownership away from the timeout controller.\n"
            "- Do not move Child into a waiting thread if the main thread still needs to kill it.\n"
            "- Keep the Child value owned by run_command and use a same-thread loop with child.try_wait(), start.elapsed() >= timeout, thread::sleep, child.kill(), and child.wait_with_output().\n"
            "- Prefer child.wait_with_output() after success or kill; it captures both stdout and stderr without separate ChildStdout/ChildStderr helper type mismatches.\n"
            "- If you write stream-reading helpers, they must accept both stdout and stderr stream types, for example by using a generic Read bound; Option<ChildStdout> cannot read ChildStderr.\n"
            "- Preserve direct Command::new(program).args(args) execution; do not use a shell.\n"
            "- Configure stdin/stdout/stderr explicitly with Stdio::null(), Stdio::piped(), and Stdio::piped() before spawn so wait_with_output captures output.\n"
            "- Filter environment with env_clear() plus only allowed_environment keys present in the provided environment map.\n"
        )
    return feedback


def write_generation_failure(
    result_path: pathlib.Path,
    case: dict,
    model: str,
    protocol: str,
    driver: str,
    failure_tag: str,
    duration_seconds: float,
    stderr: str,
) -> None:
    write_json(
        result_path,
        {
            "case_id": case["id"],
            "track": case["track"],
            "task_type": case["task_type"],
            "model": model,
            "protocol": protocol,
            "driver": driver,
            "attempt_count": 1,
            "repair_used": False,
            "hard_gates": {
                "patch_applies": False,
                "compiles": False,
                "tests_pass": False,
                "schema_valid": False,
                "scope_pass": False,
                "safety_pass": False,
                "semantic_pass": False,
            },
            "commands": [],
            "changed_files": [],
            "failure_tags": [failure_tag],
            "duration_seconds": round(duration_seconds, 3),
            "generation_error": stderr[-4000:],
        },
    )


if __name__ == "__main__":
    raise SystemExit(main())
