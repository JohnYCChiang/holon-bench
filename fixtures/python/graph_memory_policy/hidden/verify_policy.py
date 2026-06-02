import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.router import route_key


event = {
    "tenant": "acme",
    "type": "invoice.created",
    "region": "apac",
    "ulid": "01HYTAICHI0000000000000000",
}

expected = "kg-v2:apac:acme:01HYTAICHI0000000000000000"
actual = route_key(event)
if actual != expected:
    raise SystemExit(f"route_key mismatch: expected {expected!r}, got {actual!r}")
