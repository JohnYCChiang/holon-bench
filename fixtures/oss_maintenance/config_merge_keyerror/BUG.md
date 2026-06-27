# Bug report: crash when merging a config that omits the optional `limits` section

A user filed this against `merge_config`:

```
Traceback (most recent call last):
  File "app.py", line 42, in build_settings
    merged = merge_config(defaults, user_overrides)
  File "src/config.py", line 11, in merge_config
    result["effective_timeout"] = base["limits"]["timeout"] + override["limits"]["timeout"]
KeyError: 'limits'
```

Their `user_overrides` only set `{"name": "prod"}` — no `limits` section, which the
docs say is optional. Defaults always carry `limits`, so the merged timeout should
just fall back to the base value.

Expected: merging an override that omits an optional section must not crash; the
missing section contributes nothing (treat its timeout as 0).

You are the maintainer. Reproduce, fix the root cause with a minimal change, and
**leave behind a regression test** so this defect cannot come back.
