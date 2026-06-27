package loot

import "testing"

func TestRollHitsFirstRange(t *testing.T) {
	// id1 covers [0,10), id2 covers [10,30).
	tbl := Table{Entries: []Entry{{ID: 1, Weight: 10}, {ID: 2, Weight: 20}}}
	if got := Roll(tbl, 5); got != 1 {
		t.Fatalf("roll 5 = %d, want 1", got)
	}
}

func TestRollHitsSecondRange(t *testing.T) {
	tbl := Table{Entries: []Entry{{ID: 1, Weight: 10}, {ID: 2, Weight: 20}}}
	if got := Roll(tbl, 15); got != 2 {
		t.Fatalf("roll 15 = %d, want 2", got)
	}
}

func TestRollWrapsModuloTotal(t *testing.T) {
	tbl := Table{Entries: []Entry{{ID: 1, Weight: 10}, {ID: 2, Weight: 20}}}
	if got := Roll(tbl, 35); got != 1 { // 35 % 30 = 5 -> id1
		t.Fatalf("roll 35 = %d, want 1", got)
	}
}
