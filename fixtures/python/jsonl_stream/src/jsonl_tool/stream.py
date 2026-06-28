from __future__ import annotations

import json


def parse_jsonl(text):
    records = [json.loads(line) for line in text.split("\n")]
    return {"ok": True, "records": records, "count": len(records)}
