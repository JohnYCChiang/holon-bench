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
    "gemma-4-26b-moe": "/home/taichi/models/gemma-4-26B-A4B-it-UD-Q8_K_XL.gguf",
    "gemma-4-31b-q4": "/home/taichi/models/gemma-4-31B-it-UD-Q4_K_XL.gguf",
    "gemma-4-31b-q8": "/home/taichi/models/gemma-4-31B-it-UD-Q8_K_XL.gguf",
}

TRACKS = [
    "python_tool_engineering",
    "rust_core",
    "rust_porting",
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
    tracks: list[str],
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
        "--threads", "16",
        "--threads-batch", "32",
        "--ctx-size", "65536",
        "--batch-size", "2048",
        "--ubatch-size", "1024",
        "--parallel", "1",
        "--device", "Vulkan0",
        "--split-mode", "none",
        "--main-gpu", "0",
        "--n-gpu-layers", "999",
        "--fit", "on",
        "--cache-type-k", "q8_0",
        "--cache-type-v", "q8_0",
        "--flash-attn", "on",
        "--jinja",
        "--no-webui",
        "--metrics",
        "--slots",
        "--cache-ram", "0",
        "--seed", "42",
        "--temp", "0.2",
        "--top-p", "0.9",
        "--min-p", "0.0",
        "--reasoning-budget", "1024"
    ]

    log_file_path = f"/tmp/gemma_bench_{model_name}_{port}.log"
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
                "--generation-timeout-seconds", "600.0"
            ]
            
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
    parser.add_argument("--driver", choices=["direct", "holon-cli"], default="direct")
    parser.add_argument("--holon-max-iterations", type=int, default=100)
    parser.add_argument(
        "--tracks",
        default=",".join(TRACKS),
        help="Comma-separated track list. Defaults to all enabled Phase 2 tracks.",
    )
    args = parser.parse_args()

    models_to_run = list(MODELS.keys()) if args.model == "all" else [args.model]
    selected_tracks = [track.strip() for track in args.tracks.split(",") if track.strip()]
    
    all_scores = []
    for m in models_to_run:
        score_files = run_bench_for_model(
            m,
            MODELS[m],
            args.port,
            args.driver,
            args.holon_max_iterations,
            selected_tracks,
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
        
        # Print the markdown report path
        print("Check reports/model_matrix.md for the summary.")

if __name__ == "__main__":
    main()
