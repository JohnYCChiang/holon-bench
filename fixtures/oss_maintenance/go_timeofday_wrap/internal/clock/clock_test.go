package clock

import "testing"

func TestNegativeDeltaWrapsBeforeMidnight(t *testing.T) {
	if got := AddMinutes(10, -20); got != 1430 {
		t.Fatalf("AddMinutes(10, -20) = %d, want 1430", got)
	}
}
