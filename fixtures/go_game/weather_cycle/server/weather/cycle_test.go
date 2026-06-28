package weather

import "testing"

func TestPhaseHoldsForDuration(t *testing.T) {
	c := NewCycle([]string{"sun", "rain", "storm"}, 4)
	for tick := 0; tick < 4; tick++ {
		if got := c.At(tick); got != "sun" {
			t.Fatalf("At(%d)=%q want sun (phase must hold for the window)", tick, got)
		}
	}
	if got := c.At(4); got != "rain" {
		t.Fatalf("At(4)=%q want rain", got)
	}
}

func TestPhaseAdvances(t *testing.T) {
	c := NewCycle([]string{"sun", "rain", "storm"}, 4)
	if got := c.At(8); got != "storm" {
		t.Fatalf("At(8)=%q want storm", got)
	}
	if got := c.At(12); got != "sun" {
		t.Fatalf("At(12)=%q want sun (cycle wraps)", got)
	}
}
