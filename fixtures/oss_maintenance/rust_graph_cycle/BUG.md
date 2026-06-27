# Bug report: `topo_sort` accepts cyclic graphs and returns a bogus order

`topo_sort(n, edges)` topologically sorts nodes `0..n` of a directed graph
(`edges` are `(from, to)` pairs), returning `Ok(order)` for a DAG or
`Err(GraphError::Cycle)` when a directed cycle exists. A user reports that an
obvious cycle is not detected:

```
topo_sort(3, &[(0, 1), (1, 2), (2, 0)])
// got:  Ok([...])             want: Err(GraphError::Cycle)
```

The depth-first search only tracks whether a node was *ever* visited, so a
back-edge to a node still on the current DFS path is skipped and the cycle is
never reported. A self-loop `(0, 0)` is missed the same way.

Expected: a back-edge to a node on the current recursion path is a cycle; a
forward/cross edge to an already-finished node is fine. Out-of-range nodes
return `Err(GraphError::NodeOutOfRange(x))`.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`topo_sort` signature and the `GraphError` variants), and **leave behind a
regression test**.
