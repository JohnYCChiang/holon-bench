package hitstop

import "testing"

func TestHitAddsFreeze(t *testing.T) {
	out := Apply(State{Frozen: 0, Max: 10}, Input{HitFreeze: 6})
	if out.Frozen != 6 {
		t.Fatalf("frozen = %d, want 6", out.Frozen)
	}
}

func TestAccumulationCappedAtMax(t *testing.T) {
	out := Apply(State{Frozen: 8, Max: 10}, Input{HitFreeze: 5})
	if out.Frozen != 10 {
		t.Fatalf("frozen = %d, want 10", out.Frozen)
	}
}

func TestNoHitTicksDown(t *testing.T) {
	out := Apply(State{Frozen: 4, Max: 10}, Input{})
	if out.Frozen != 3 {
		t.Fatalf("frozen = %d, want 3", out.Frozen)
	}
}
