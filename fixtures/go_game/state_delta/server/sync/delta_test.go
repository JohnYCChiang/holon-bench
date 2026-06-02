package sync

import "testing"

func TestBuildDeltaIncludesOnlyChangedNewAndRemoved(t *testing.T) {
	prev := map[string]Entity{
		"a": {X: 1, Y: 1},
		"b": {X: 2, Y: 2},
		"gone": {X: 9, Y: 9},
	}
	next := map[string]Entity{
		"a": {X: 1, Y: 1},
		"b": {X: 3, Y: 2},
		"new": {X: 0, Y: 1},
	}
	delta := BuildDelta(prev, next)
	if _, ok := delta.Changed["a"]; ok {
		t.Fatalf("unchanged entity included: %#v", delta.Changed)
	}
	if delta.Changed["b"] != (Entity{X: 3, Y: 2}) || delta.Changed["new"] != (Entity{X: 0, Y: 1}) {
		t.Fatalf("changed = %#v", delta.Changed)
	}
	if len(delta.Removed) != 1 || delta.Removed[0] != "gone" {
		t.Fatalf("removed = %#v, want gone", delta.Removed)
	}
}
