from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    crate_root = Path.cwd()
    with tempfile.TemporaryDirectory() as tmp:
        probe = Path(tmp)
        write(
            probe / "Cargo.toml",
            f"""[package]
name = "module_visibility_probe"
version = "0.1.0"
edition = "2021"

[dependencies]
module_visibility = {{ path = "{crate_root}" }}
""",
        )
        write(
            probe / "src/lib.rs",
            """use module_visibility::{parse_command, Command};
use module_visibility::internal;

pub fn probe() -> Command {
    let parsed = parse_command("run alpha");
    let _ = internal::parse("leaked");
    parsed
}
""",
        )

        result = subprocess.run(
            ["cargo", "check", "--quiet"],
            cwd=probe,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )
        if result.returncode == 0:
            print("internal module is publicly accessible")
            return 1
        if "module `internal` is private" not in result.stderr and "private module" not in result.stderr:
            print(result.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
