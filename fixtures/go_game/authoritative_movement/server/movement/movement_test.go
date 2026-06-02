package movement

import "testing"

func TestRejectsMovementOverMaxStep(t *testing.T) {
	stats := &Stats{}
	pos := Position{X: 0, Y: 0}
	pos = Apply(pos, Position{X: 2, Y: 1}, 3, stats)
	pos = Apply(pos, Position{X: 99, Y: 1}, 3, stats)

	if pos != (Position{X: 2, Y: 1}) {
		t.Fatalf("position = %#v, want previous accepted position", pos)
	}
	if stats.Accepted != 1 || stats.Rejected != 1 {
		t.Fatalf("stats = %#v, want 1 accepted 1 rejected", stats)
	}
}
