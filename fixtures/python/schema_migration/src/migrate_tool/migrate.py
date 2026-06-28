from __future__ import annotations


def migrate(record, target_version, migrations):
    version = record["version"]
    if version in migrations:
        record = migrations[version](record)
        record["version"] = version + 1
    record["version"] = target_version
    return {"ok": True, "record": record, "applied": [version], "version": target_version}
