package hitreg

import "testing"

func seed() *History {
	h := NewHistory(8)
	h.Record(Pos{Tick: 1, X: 0, Y: 0})
	h.Record(Pos{Tick: 2, X: 10, Y: 0})
	h.Record(Pos{Tick: 3, X: 20, Y: 0})
	return h
}

func TestRewindUsesHistoricalPosition(t *testing.T) {
	h := seed()
	// at tick 1 the target was at (0,0); a shot there is a hit
	if !h.ValidateHit(1, 0, 0, 2) {
		t.Fatal("valid historical hit rejected")
	}
	// the target is NOW at (20,0); a shot at (20,0) claiming tick 1 must miss
	if h.ValidateHit(1, 20, 0, 2) {
		t.Fatal("server trusted current position instead of rewound one")
	}
}

func TestUnknownTickRejected(t *testing.T) {
	h := seed()
	if _, ok := h.PositionAt(99); ok {
		t.Fatal("unknown tick must not resolve")
	}
	if h.ValidateHit(99, 20, 0, 5) {
		t.Fatal("hit at an unrecorded tick must be rejected")
	}
}
