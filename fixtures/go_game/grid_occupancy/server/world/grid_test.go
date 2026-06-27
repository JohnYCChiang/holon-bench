package world

import "testing"

func TestMoveRejectedOntoOccupied(t *testing.T) {
	g := NewGrid()
	if !g.Spawn("a", 0, 0) {
		t.Fatal("spawn a")
	}
	if !g.Spawn("b", 1, 0) {
		t.Fatal("spawn b")
	}
	if g.Move("a", 1, 0) {
		t.Fatal("move onto b must be rejected")
	}
	if g.At(0, 0) != "a" {
		t.Fatalf("a should stay at 0,0; got %q", g.At(0, 0))
	}
	if g.At(1, 0) != "b" {
		t.Fatalf("b should stay; got %q", g.At(1, 0))
	}
}

func TestMoveToFreeCell(t *testing.T) {
	g := NewGrid()
	g.Spawn("a", 0, 0)
	if !g.Move("a", 2, 2) {
		t.Fatal("move to free cell")
	}
	if g.At(0, 0) != "" {
		t.Fatal("old cell freed")
	}
	if g.At(2, 2) != "a" {
		t.Fatal("new cell occupied")
	}
}
