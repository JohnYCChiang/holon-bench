package loot

import (
	"reflect"
	"sort"
	"testing"
)

func TestRollLootDeterministicAcrossInsertionOrder(t *testing.T) {
	ids := []string{"alice", "bob", "carol", "dave", "erin", "frank"}
	m1 := map[string]int{}
	for _, id := range ids {
		m1[id] = 1
	}
	m2 := map[string]int{}
	for i := len(ids) - 1; i >= 0; i-- {
		m2[ids[i]] = 1
	}
	a := RollLoot(42, m1, 6)
	b := RollLoot(42, m2, 6)
	if !reflect.DeepEqual(a, b) {
		t.Fatalf("loot not deterministic across map order:\n a=%v\n b=%v", a, b)
	}
}

func TestRollLootSortedAndVaried(t *testing.T) {
	m := map[string]int{}
	for _, id := range []string{"p3", "p1", "p2", "p5", "p4", "p6", "p7", "p8"} {
		m[id] = 1
	}
	out := RollLoot(7, m, 6)
	if !sort.SliceIsSorted(out, func(i, j int) bool { return out[i].Player < out[j].Player }) {
		t.Fatalf("output not sorted by player: %v", out)
	}
	allSame := true
	for _, d := range out {
		if d.Index != out[0].Index {
			allSame = false
		}
		if d.Index < 0 || d.Index >= 6 {
			t.Fatalf("index out of range: %d", d.Index)
		}
	}
	if allSame {
		t.Fatal("all loot indices identical -> RNG not advancing")
	}
}
