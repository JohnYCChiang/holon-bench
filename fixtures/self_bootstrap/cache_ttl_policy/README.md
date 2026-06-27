# Self-bootstrap fixture: cache TTL policy

`engine.py` is a frozen TTL resolver. It reads `ttl.json` and returns the cache
lifetime (seconds) for a resource type, falling back to `default_ttl`:

```
get_ttl(config, resource) -> int
```

The volatile `auth_token` resource currently inherits the long `default_ttl`,
so stale tokens are served. Give `auth_token` a short TTL (greater than 0 and at
most 60 seconds) without shortening the long-lived resources or the default:
`static_asset`, `user_profile`, and `default_ttl` must keep their current values.

You may only edit `ttl.json`. Do not edit `engine.py` or any test.
