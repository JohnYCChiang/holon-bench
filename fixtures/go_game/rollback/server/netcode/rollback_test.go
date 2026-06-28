package netcode

import "testing"

func TestStateIndependentOfApplyOrder(t *testing.T) {
	a := NewEngine(10)
	a.Apply(Input{Tick: 1, Player: "p1", Delta: 5})
	a.Apply(Input{Tick: 2, Player: "p2", Delta: 7})
	a.Apply(Input{Tick: 3, Player: "p1", Delta: -2})

	b := NewEngine(10)
	b.Apply(Input{Tick: 3, Player: "p1", Delta: -2})
	b.Apply(Input{Tick: 1, Player: "p1", Delta: 5})
	b.Apply(Input{Tick: 2, Player: "p2", Delta: 7})

	if a.State() != b.State() {
		t.Fatalf("state depends on arrival order: %d vs %d", a.State(), b.State())
	}
	if a.State() != 10 {
		t.Fatalf("state=%d want 10", a.State())
	}
}

func TestDuplicateInputRejected(t *testing.T) {
	e := NewEngine(10)
	if !e.Apply(Input{Tick: 1, Player: "p1", Delta: 5}) {
		t.Fatal("first apply should succeed")
	}
	if e.Apply(Input{Tick: 1, Player: "p1", Delta: 5}) {
		t.Fatal("duplicate (tick,player) must be rejected")
	}
	if e.State() != 5 {
		t.Fatalf("duplicate double-applied: state=%d", e.State())
	}
}
