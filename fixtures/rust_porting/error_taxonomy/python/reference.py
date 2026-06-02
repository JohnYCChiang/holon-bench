#!/usr/bin/env python3
import sys

mapping = {
    "timeout": ("timeout", True),
    "rate": ("rate_limited", True),
    "validation": ("validation", False),
    "not_found": ("not_found", False),
}
code, retryable = mapping.get(sys.argv[1], ("internal_error", False))
print(f"{code}|{str(retryable).lower()}")
