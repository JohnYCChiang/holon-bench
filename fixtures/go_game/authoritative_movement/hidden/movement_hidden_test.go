package movement

import "testing"

func TestHiddenRejectedMovementPreservesAuthoritativeStateForNextInput(t *testing.T) {
	stats := &Stats{}
	pos := Position{X: 10, Y: 10}

	pos = Apply(pos, Position{X: 10, Y: 7}, 3, stats)
	if pos != (Position{X: 10, Y: 7}) {
		t.Fatalf("boundary negative move position = %#v", pos)
	}

	pos = Apply(pos, Position{X: 10, Y: 3}, 3, stats)
	if pos != (Position{X: 10, Y: 7}) {
		t.Fatalf("rejected move changed authoritative position to %#v", pos)
	}

	pos = Apply(pos, Position{X: 8, Y: 7}, 3, stats)
	if pos != (Position{X: 8, Y: 7}) {
		t.Fatalf("valid move after rejection used wrong base position: %#v", pos)
	}

	if stats.Accepted != 2 || stats.Rejected != 1 {
		t.Fatalf("stats = %#v, want 2 accepted 1 rejected", stats)
	}
}
