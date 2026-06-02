import hashlib
import json
import sys

SALT = "holon-cache-v2:"


def normalize(value):
    if isinstance(value, dict):
        return {key: normalize(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if isinstance(value, str):
        return value.strip()
    return value


payload = normalize(json.loads(sys.argv[1]))
canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
print(hashlib.sha256((SALT + canonical).encode()).hexdigest())
