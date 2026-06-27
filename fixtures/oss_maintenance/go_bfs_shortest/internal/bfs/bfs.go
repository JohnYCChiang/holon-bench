package bfs

// ShortestPath returns the number of edges on a shortest path from src to dst in
// an undirected graph with nodes 0..n-1. It returns 0 when src == dst and -1 when
// dst is unreachable or either endpoint is out of range. edges is a list of
// {u, v} pairs.
func ShortestPath(n int, edges [][2]int, src, dst int) int {
	if src < 0 || src >= n || dst < 0 || dst >= n {
		return -1
	}
	adj := make([][]int, n)
	for _, e := range edges {
		u, v := e[0], e[1]
		if u < 0 || u >= n || v < 0 || v >= n {
			continue
		}
		adj[u] = append(adj[u], v)
		adj[v] = append(adj[v], u)
	}
	dist := map[int]int{src: 0}
	visited := map[int]bool{src: true}
	frontier := []int{src}
	for len(frontier) > 0 {
		// BUG: pops from the END (LIFO / stack) -> this is depth-first, not
		// breadth-first, so the first time dst is reached is not via a shortest
		// path and the returned distance can be too large.
		cur := frontier[len(frontier)-1]
		frontier = frontier[:len(frontier)-1]
		if cur == dst {
			return dist[cur]
		}
		for _, nb := range adj[cur] {
			if !visited[nb] {
				visited[nb] = true
				dist[nb] = dist[cur] + 1
				frontier = append(frontier, nb)
			}
		}
	}
	return -1
}
