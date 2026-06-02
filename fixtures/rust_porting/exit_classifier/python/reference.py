#!/usr/bin/env python3
import sys

code = int(sys.argv[1])
if code == 0:
    print("success|false")
elif code == 2:
    print("usage_error|false")
elif code < 0:
    print("interrupted|true")
else:
    print("failed|true")
