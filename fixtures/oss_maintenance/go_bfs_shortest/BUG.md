# Bug report: `ShortestPath` sometimes returns a longer-than-shortest distance

`bfs.ShortestPath` should return the number of edges on a **shortest** path
between two nodes of an undirected graph. A user reports an inflated distance:

```
// edges: 0-1, 1-4, 0-2, 2-3, 3-4   (routes 0->4 are length 2 and length 3)
ShortestPath(5, edges, 0, 4)
// got:  3
// want: 2
```

The traversal pops the **most recently** added node from its frontier slice,
turning the intended breadth-first search into a depth-first one. Depth-first may
reach the destination via a longer route first, so the recorded distance is not
the shortest.

Expected: nodes are expanded in breadth-first (FIFO) order, so the first time the
destination is reached is along a shortest path. `src == dst` returns 0;
unreachable or out-of-range returns -1.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`ShortestPath` signature), and **leave behind a regression test**.
