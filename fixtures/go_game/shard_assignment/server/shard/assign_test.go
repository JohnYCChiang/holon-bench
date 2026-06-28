package shard

import "testing"

func TestCapacityNotExceeded(t *testing.T) {
	c := NewCluster([]string{"s0", "s1"}, 1)
	for _, p := range []string{"alice", "bob", "carol"} {
		c.Assign(p)
	}
	for _, s := range []string{"s0", "s1"} {
		if c.Load(s) > 1 {
			t.Fatalf("shard %s overfilled: load=%d", s, c.Load(s))
		}
	}
}

func TestFullClusterRejects(t *testing.T) {
	c := NewCluster([]string{"only"}, 1)
	if _, ok := c.Assign("a"); !ok {
		t.Fatal("first assign should succeed")
	}
	if _, ok := c.Assign("b"); ok {
		t.Fatal("assign into a full cluster must fail")
	}
}
