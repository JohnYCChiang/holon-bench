#!/usr/bin/env python3
import sys
from pathlib import Path

dry_run = sys.argv[1] == "true"
deleted = 0
would_delete = []
skipped = []
for raw in sorted(sys.argv[2:]):
    path = Path(raw)
    if not path.exists():
        skipped.append(path.name)
    elif dry_run:
        would_delete.append(path.name)
    else:
        path.unlink()
        deleted += 1
print(f"deleted={deleted};would={','.join(would_delete)};skipped={','.join(skipped)}")
