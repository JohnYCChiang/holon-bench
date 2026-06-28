package presence

import (
	"reflect"
	"testing"
)

func TestSweepBoundaryInclusive(t *testing.T) {
	tr := NewTracker(10)
	tr.Touch("a", 0)
	out := tr.Sweep(10) // now-last == timeout -> AFK
	if !reflect.DeepEqual(out, []string{"a"}) {
		t.Fatalf("boundary not inclusive: %v", out)
	}
}

func TestSweepSortedAndRemoves(t *testing.T) {
	tr := NewTracker(5)
	tr.Touch("z", 0)
	tr.Touch("a", 0)
	tr.Touch("m", 0)
	out := tr.Sweep(5)
	if !reflect.DeepEqual(out, []string{"a", "m", "z"}) {
		t.Fatalf("not sorted: %v", out)
	}
	if again := tr.Sweep(100); len(again) != 0 {
		t.Fatalf("swept players returned again: %v", again)
	}
}
