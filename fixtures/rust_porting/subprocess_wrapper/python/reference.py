import json
import os
import subprocess
import sys


def run(env_value: str) -> dict:
    env = {"PORT_ALLOWED": env_value}
    completed = subprocess.run(
        [sys.executable, "-c", "import os; print(os.environ.get('PORT_ALLOWED', '')); print(os.environ.get('PORT_SECRET', 'missing'))"],
        capture_output=True,
        text=True,
        env=env,
    )
    return {
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "exit_code": completed.returncode,
        "timed_out": False,
    }


print(json.dumps(run(sys.argv[1]), sort_keys=True))
