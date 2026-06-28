package objective

import "testing"

func TestCaptureRejectsInvalidPoint(t *testing.T) {
	m := NewMatch([]string{"A", "B"})
	if m.Capture("ghost", "red") {
		t.Fatal("capturing an unregistered point must be rejected")
	}
	m.Tick()
	if m.Score("red") != 0 {
		t.Fatalf("rejected capture must not score: %d", m.Score("red"))
	}
}

func TestCaptureRejectsEmptyTeam(t *testing.T) {
	m := NewMatch([]string{"A"})
	if m.Capture("A", "") {
		t.Fatal("empty team must be rejected")
	}
}
