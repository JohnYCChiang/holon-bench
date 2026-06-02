import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.review import review_change


warnings = review_change(
    {
        "amount": 10,
        "account_state": "settled",
        "operation": "mutation",
        "source": "external_api",
    }
)

required = "ADR-42 forbids external mutation of settled accounts"
if required not in warnings:
    raise SystemExit(f"missing graph-derived review warning: {required!r}; got {warnings!r}")
