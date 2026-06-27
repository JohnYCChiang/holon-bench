package retarget

import "testing"

func TestPicksHighestThreatLiving(t *testing.T) {
	got := Retarget([]Unit{{1, 10, true}, {2, 30, true}, {3, 20, true}}, -1)
	if got != 2 {
		t.Fatalf("target = %d, want 2", got)
	}
}

func TestExcludesUnitThatJustDied(t *testing.T) {
	got := Retarget([]Unit{{1, 10, true}, {2, 30, true}, {3, 20, true}}, 2)
	if got != 3 {
		t.Fatalf("target = %d, want 3", got)
	}
}

func TestExcludesDeadFlag(t *testing.T) {
	got := Retarget([]Unit{{1, 50, false}, {2, 20, true}}, -1)
	if got != 2 {
		t.Fatalf("target = %d, want 2", got)
	}
}
