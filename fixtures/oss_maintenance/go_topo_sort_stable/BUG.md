# Bug report: `Sort` is not a STABLE topological sort

`toposort.Sort(nodes, edges)` returns a topological ordering of `nodes`. The
contract says that when several nodes are simultaneously ready (no remaining
incoming edges), they must be emitted in their original order within `nodes`. A
user reports the input order being lost:

```
Sort([]string{"b", "a"}, nil)
// got:  [a b]
// want: [b a]
```

The implementation breaks ties by sorting the ready set alphabetically
(`sort.Strings`) instead of preserving each node's position in `nodes`.

Expected: ready nodes are emitted in input order; edges are still respected; a
cycle returns `ErrCycle`.

You are the maintainer. Reproduce, fix the root cause minimally (keep the `Sort`
signature, the `ErrCycle` sentinel, and cycle detection), and **leave behind a
regression test**.
