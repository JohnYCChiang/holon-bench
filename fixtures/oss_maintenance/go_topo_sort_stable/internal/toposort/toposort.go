package toposort

import (
	"errors"
	"sort"
)

// ErrCycle is returned when the graph cannot be linearized.
var ErrCycle = errors.New("toposort: cycle detected")

// Sort returns a topological ordering of nodes given directed edges {from, to}.
// When several nodes are simultaneously ready (no remaining incoming edges),
// they must be emitted in their original order within nodes (a STABLE topo
// sort). A cycle yields ErrCycle.
func Sort(nodes []string, edges [][2]string) ([]string, error) {
	indeg := make(map[string]int, len(nodes))
	adj := make(map[string][]string)
	for _, n := range nodes {
		indeg[n] = 0
	}
	for _, e := range edges {
		adj[e[0]] = append(adj[e[0]], e[1])
		indeg[e[1]]++
	}

	var ready []string
	for n := range indeg {
		if indeg[n] == 0 {
			ready = append(ready, n)
		}
	}
	// BUG: the tie-break orders ready nodes alphabetically instead of by their
	// position in nodes, so a stable input order is not preserved
	// (Sort([]string{"b","a"}, nil) returns ["a","b"] instead of ["b","a"]).
	sort.Strings(ready)

	out := make([]string, 0, len(nodes))
	for len(ready) > 0 {
		n := ready[0]
		ready = ready[1:]
		out = append(out, n)
		var next []string
		for _, m := range adj[n] {
			indeg[m]--
			if indeg[m] == 0 {
				next = append(next, m)
			}
		}
		sort.Strings(next)
		ready = append(ready, next...)
	}

	if len(out) != len(nodes) {
		return nil, ErrCycle
	}
	return out, nil
}
