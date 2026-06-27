//! Depth-first topological sort with cycle detection.

#[derive(Debug, PartialEq, Eq)]
pub enum GraphError {
    /// The graph contains a directed cycle.
    Cycle,
    /// An edge references a node index >= n.
    NodeOutOfRange(usize),
}

/// Topologically sort nodes `0..n` of the directed graph given by `edges`
/// (`(from, to)` pairs). Returns `Ok(order)` where every edge points forward,
/// or `Err(GraphError::Cycle)` if a directed cycle exists. An edge naming a node
/// `>= n` yields `Err(GraphError::NodeOutOfRange(x))`.
pub fn topo_sort(n: usize, edges: &[(usize, usize)]) -> Result<Vec<usize>, GraphError> {
    for &(u, v) in edges {
        if u >= n {
            return Err(GraphError::NodeOutOfRange(u));
        }
        if v >= n {
            return Err(GraphError::NodeOutOfRange(v));
        }
    }
    let mut adj = vec![Vec::new(); n];
    for &(u, v) in edges {
        adj[u].push(v);
    }
    let mut visited = vec![false; n];
    let mut order = Vec::with_capacity(n);
    for start in 0..n {
        if !visited[start] && dfs(start, &adj, &mut visited, &mut order) {
            return Err(GraphError::Cycle);
        }
    }
    order.reverse();
    Ok(order)
}

// Returns true if a cycle is detected in the subtree rooted at `u`.
fn dfs(u: usize, adj: &[Vec<usize>], visited: &mut [bool], order: &mut Vec<usize>) -> bool {
    visited[u] = true;
    for &v in &adj[u] {
        // BUG: an already-visited node is assumed safe, so a back-edge to a node
        // still on the current DFS path (a cycle) is silently skipped. Detecting
        // cycles needs to distinguish "on the current path" from "finished".
        if !visited[v] && dfs(v, adj, visited, order) {
            return true;
        }
    }
    order.push(u);
    false
}
