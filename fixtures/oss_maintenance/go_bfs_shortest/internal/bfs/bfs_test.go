package bfs

import "testing"

func TestReturnsShortestNotDepthFirst(t *testing.T) {
	// Two routes 0->4: 0-1-4 (len 2) and 0-2-3-4 (len 3). A stack-based
	// traversal explores the long route first and returns 3.
	edges := [][2]int{{0, 1}, {1, 4}, {0, 2}, {2, 3}, {3, 4}}
	if got := ShortestPath(5, edges, 0, 4); got != 2 {
		t.Fatalf("ShortestPath = %d, want 2", got)
	}
}
