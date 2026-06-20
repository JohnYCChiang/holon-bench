#!/usr/bin/env python3
"""Reusable consumer/guard for the governance matrix artifact (M17).

M15 froze the matrix output as a stable, machine-consumable contract tagged
``schema_version: "governance-matrix/v1"`` and stated that *consumers should reject
any document whose schema_version they do not recognize*. That claim only has teeth
if a real consumer enforces it. This module is that consumer: it loads a
``governance-matrix/v1`` artifact and **fails closed** on an unrecognized
``schema_version`` or a malformed shape, so the contract is exercised, not just
asserted inline.

It deliberately validates the *contract envelope*, not the governance verdict: by
default a well-formed ``ok: false`` matrix is a recognized, valid document (a
consumer may still want to read its failing rows). Pass ``--require-ok`` to also
require ``ok is true`` -- that is the mode world health uses, where a non-ok matrix
must fail the check.

This is offline and pure: it reads one JSON file and inspects it. It runs no smoke,
no subprocess, and no live process.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

# Schema versions this consumer understands. A document tagged with anything else
# is rejected: bumping the matrix's shape must be a deliberate, recognized change
# here, never a silent accept. Mirrors SCHEMA_VERSION in holon_governance_matrix.py
# and schemas/governance_matrix.schema.json.
RECOGNIZED_SCHEMA_VERSIONS = frozenset({"governance-matrix/v1"})

REQUIRED_TOP_LEVEL_KEYS = ("schema_version", "matrix", "ok", "row_count", "rows")


def verify(doc: Any, *, require_ok: bool = False) -> list[str]:
    """Return a list of contract violations (empty list == document accepted)."""
    errors: list[str] = []

    if not isinstance(doc, dict):
        return [f"document is not a JSON object (got {type(doc).__name__})"]

    # schema_version is the gate: an unrecognized version is rejected before any
    # further shape assumptions, since those assumptions only hold for known
    # versions.
    version = doc.get("schema_version")
    if version not in RECOGNIZED_SCHEMA_VERSIONS:
        errors.append(
            f"unrecognized schema_version {version!r} "
            f"(recognized: {sorted(RECOGNIZED_SCHEMA_VERSIONS)})"
        )

    missing = [key for key in REQUIRED_TOP_LEVEL_KEYS if key not in doc]
    if missing:
        errors.append(f"missing required top-level keys: {missing}")

    if "ok" in doc and not isinstance(doc["ok"], bool):
        errors.append(f"'ok' must be a boolean (got {type(doc['ok']).__name__})")

    rows = doc.get("rows")
    if "rows" in doc and not isinstance(rows, list):
        errors.append(f"'rows' must be a list (got {type(rows).__name__})")
    elif isinstance(rows, list) and "row_count" in doc and doc["row_count"] != len(rows):
        errors.append(
            f"row_count {doc['row_count']} != actual number of rows {len(rows)}"
        )

    if require_ok and doc.get("ok") is not True:
        errors.append(f"matrix is not ok (ok={doc.get('ok')!r}) but --require-ok set")

    return errors


def load(path: pathlib.Path) -> Any:
    """Load and JSON-parse an artifact, raising ValueError with a clear message."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as err:
        raise ValueError(f"cannot read artifact {path}: {err}") from err
    try:
        return json.loads(text)
    except json.JSONDecodeError as err:
        raise ValueError(f"artifact {path} is not valid JSON: {err}") from err


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        help="path to a governance-matrix/v1 JSON artifact (e.g. from --out)",
    )
    parser.add_argument(
        "--require-ok",
        action="store_true",
        help="also require the matrix verdict to be ok (ok == true)",
    )
    args = parser.parse_args(argv)

    try:
        doc = load(pathlib.Path(args.path))
    except ValueError as err:
        print(f"holon_governance_matrix_consume: {err}", file=sys.stderr)
        return 1

    errors = verify(doc, require_ok=args.require_ok)
    if errors:
        print(
            "holon_governance_matrix_consume: rejected "
            f"({len(errors)} contract violation(s))",
            file=sys.stderr,
        )
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(
        "holon_governance_matrix_consume: ok "
        f"(recognized {doc['schema_version']}, {doc['row_count']} rows"
        + (", verdict ok" if args.require_ok else "")
        + ")"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
