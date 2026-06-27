"""Frozen label taxonomy. Do not edit — only the category map changes."""
from __future__ import annotations

import json
import pathlib


def load_taxonomy(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "taxonomy.json"
    return json.loads(target.read_text(encoding="utf-8"))


def category_of(tax: dict, tag: str) -> str:
    """First category whose tag list contains the tag, else 'uncategorized'."""
    for category, tags in tax.get("categories", {}).items():
        if tag in tags:
            return category
    return "uncategorized"
