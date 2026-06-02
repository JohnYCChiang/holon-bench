import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.banner import support_banner


expected = "support: holon-local-uma"
actual = support_banner()
if actual != expected:
    raise SystemExit(f"wrong scoped memory used: expected {expected!r}, got {actual!r}")
