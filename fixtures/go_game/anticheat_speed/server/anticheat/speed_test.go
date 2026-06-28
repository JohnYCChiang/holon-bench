package anticheat

import "testing"

func TestRejectsTeleport(t *testing.T) {
	v := NewValidator(5)
	v.Spawn("a", 0, 0, 0)
	if v.Update("a", 100, 0, 1) {
		t.Fatal("a 100-unit jump in one tick must be rejected")
	}
	x, y := v.Pos("a")
	if x != 0 || y != 0 {
		t.Fatalf("rejected update moved player to %d,%d", x, y)
	}
}

func TestAcceptsLegalMove(t *testing.T) {
	v := NewValidator(5)
	v.Spawn("a", 0, 0, 0)
	if !v.Update("a", 3, 2, 1) {
		t.Fatal("a 5-unit move in one tick is legal")
	}
}
