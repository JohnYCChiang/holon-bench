import json
import pathlib
import sys


def scan(root: str, excluded_suffix: str) -> dict:
    base = pathlib.Path(root)
    files = []
    skipped = {"hidden": 0, "ignored": 0}
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(base).as_posix()
        if any(part.startswith(".") for part in path.relative_to(base).parts):
            skipped["hidden"] += 1
        elif rel.endswith(excluded_suffix):
            skipped["ignored"] += 1
        else:
            files.append(rel)
    return {"files": sorted(files), "skipped": skipped}


print(json.dumps(scan(sys.argv[1], sys.argv[2]), sort_keys=True))
