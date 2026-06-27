# Bug report: LRU cache evicts a freshly-read key

`LRUCache(capacity)` is a fixed-size cache that should evict the **least
recently used** entry. The docs say both `get` and `put` count as a use, so a
key you just read should survive the next insert. A user reports the opposite:

```
c = LRUCache(2)
c.put("a", 1)
c.put("b", 2)
c.get("a")        # read "a": it should now be most-recently used
c.put("c", 3)     # cache full -> should evict "b" (the LRU), keeping "a"
c.get("a")        # got: None   want: 1
c.get("b")        # got: 1      want: None
```

A successful `get` is not refreshing the entry's recency, so eviction order is
driven only by insertion and the wrong key is dropped.

Expected: a successful `get` marks the key most-recently used; eviction always
removes the genuinely least-recently used entry.

You are the maintainer. Reproduce, fix the root cause with a minimal change,
and **leave behind a regression test** so this defect cannot come back.
