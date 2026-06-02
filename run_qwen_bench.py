#!/usr/bin/env python3
import argparse
import subprocess
import time
import urllib.request
import urllib.error
import sys
import os
import pathlib

# Resolve paths relative to this script's location, regardless of cwd
BENCH_DIR = pathlib.Path(__file__).parent.resolve()
RUNNERS_DIR = BENCH_DIR / "runners"

MODELS = {
    "qwen36-35b-a3b-mtp-q8": "/home/taichi/models/Qwen3.6-35B-A3B-MTP-UD-Q8_K_XL.gguf",
    "qwen36-35b-a3b-q8": "/home/taichi/models/Qwen3.6-35B-A3B-UD-Q8_K_XL.gguf",
}

TRACKS = [
    "python_tool_engineering",
    "rust_core",
    "rust_porting",
    "graph_memory_workflow",
    "rust_bevy",
    "go_core",
    "go_game_server",
    "flutter_cross_platform",
]

SERVER_BIN = "/home/taichi/llama.cpp-new/build-vulkan/bin/llama-server"

def wait_for_health(port: int, timeout_sec: int = 180) -> bool:
    url = f"http://127.0.0.1:{port}/health"
    print(f"Waiting for server to become ready at {url}...")
    start_time = time.monotonic()
    while time.monotonic() - start_time < timeout_sec:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    print("Server is ready!")
                    return True
        except Exception:
            pass
        time.sleep(2)
    print("Server failed to become ready in time.")
    return False

def run_bench_for_model(
    model_name: str,
    model_path: str,
    port: int,
    driver: str,
    holon_max_iterations: int,
    repair_attempts: int,
    tracks: list[str],
    case_ids: list[str],
) -> list[str]:
    print("=" * 60)
    print(f"STARTING BENCHMARK FOR MODEL: {model_name}")
    print(f"Model path: {model_path}")
    print("=" * 60)

    server_cmd = [
        SERVER_BIN,
        "-m", model_path,
        "--alias", model_name,
        "--host", "127.0.0.1",
        "--port", str(port),
        "--threads", "8",
        "--threads-batch", "16",
        "--ctx-size", "16384",
        "--batch-size", "8192",
        "--ubatch-size", "4096",
        "--parallel", "1",
        "--cont-batching",
        "--device", "Vulkan0",
        "--split-mode", "none",
        "--main-gpu", "0",
        "--n-gpu-layers", "999",
        "--fit", "on",
        "--fit-target", "256",
        "--no-mmap",
        "--mlock",
        "--cache-type-k", "q8_0",
        "--cache-type-v", "q8_0",
        "--cache-reuse", "256",
        "--flash-attn", "on",
        "--jinja",
        "--no-webui",
        "--metrics",
        "--slots",
        "--cache-ram", "8192",
        "--seed", "42",
        "--temp", "0.2",
        "--top-p", "0.9",
        "--min-p", "0.0",
        "--reasoning", "on",
        "--reasoning-budget", "2048"
    ]

    if "mtp" in model_name:
        server_cmd.extend([
            "--spec-type", "draft-mtp",
            "--spec-draft-ngl", "999",
            "--spec-draft-n-max", "2"
        ])

    log_file_path = f"/tmp/qwen_bench_{model_name}_{port}.log"
    print(f"Server log will be written to: {log_file_path}")
    
    # Start the llama-server
    with open(log_file_path, "w") as log_file:
        proc = subprocess.Popen(
            server_cmd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid
        )

    score_files = []
    try:
        if not wait_for_health(port):
            # Print tail of log
            print("--- Server log tail ---")
            subprocess.run(["tail", "-n", "30", log_file_path])
            raise RuntimeError("Server startup failed.")

        # Run tracks
        import shutil
        for track in tracks:
            shutil.rmtree("/tmp/holon-bench-track", ignore_errors=True)
            print("-" * 50)
            print(f"Running track: {track} on {model_name}...")
            print("-" * 50)
            
            run_cmd = [
                sys.executable,
                str(RUNNERS_DIR / "run_track.py"),
                track,
                "--model", model_name,
                "--endpoint", f"http://127.0.0.1:{port}/v1",
                "--bench-root", str(BENCH_DIR),
                "--protocol", "artifact",
                "--driver", driver,
                "--holon-max-iterations", str(holon_max_iterations),
                "--generation-timeout-seconds", "600.0",
                "--repair-attempts", str(repair_attempts),
            ]
            if case_ids:
                run_cmd.extend(["--case-ids", ",".join(case_ids)])
            
            completed = subprocess.run(run_cmd, check=False)
            print(f"Track {track} finished with return code {completed.returncode}")

    finally:
        print(f"Terminating server for {model_name}...")
        try:
            # Kill process group
            os.killpg(os.getpgid(proc.pid), 15)
            proc.wait(timeout=10)
        except Exception as e:
            print(f"Error terminating server: {e}")
            try:
                proc.kill()
            except Exception:
                pass

    # Collect score files for reporting
    reports_dir = BENCH_DIR / "reports"
    for path in reports_dir.glob(f"{model_name}_{driver}_artifact_*_score.json"):
        score_files.append(str(path))

    return score_files

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=list(MODELS.keys()) + ["all"], default="all")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--driver", choices=["direct", "holon-cli", "claw-cli"], default="direct")
    parser.add_argument("--holon-max-iterations", type=int, default=100)
    parser.add_argument(
        "--repair-attempts",
        type=int,
        default=0,
        help="Number of verifier-feedback repair attempts per case.",
    )
    parser.add_argument(
        "--tracks",
        default=",".join(TRACKS),
        help="Comma-separated track list. Defaults to all enabled Phase 2 tracks.",
    )
    parser.add_argument(
        "--case-ids",
        default="",
        help="Comma-separated case ids to run. Defaults to every case in the selected tracks.",
    )
    args = parser.parse_args()

    models_to_run = list(MODELS.keys()) if args.model == "all" else [args.model]
    selected_tracks = [track.strip() for track in args.tracks.split(",") if track.strip()]
    selected_case_ids = [case_id.strip() for case_id in args.case_ids.split(",") if case_id.strip()]
    
    all_scores = []
    for m in models_to_run:
        score_files = run_bench_for_model(
            m,
            MODELS[m],
            args.port,
            args.driver,
            args.holon_max_iterations,
            args.repair_attempts,
            selected_tracks,
            selected_case_ids,
        )
        all_scores.extend(score_files)
        time.sleep(5) # Let system cool down

    if all_scores:
        print("=" * 60)
        print("GENERATING COMBINED MATRIX REPORT...")
        print("=" * 60)
        report_cmd = [
            sys.executable,
            str(RUNNERS_DIR / "report.py"),
            *all_scores,
            "--bench-root", str(BENCH_DIR)
        ]
        subprocess.run(report_cmd, check=True)
        print("Report compiled successfully!")
        print("Check reports/model_matrix.md for the summary.")

if __name__ == "__main__":
    main()
