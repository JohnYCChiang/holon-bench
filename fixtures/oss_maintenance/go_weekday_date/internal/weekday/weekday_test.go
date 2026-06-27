package weekday

import "testing"

func TestJanuaryAdjustment(t *testing.T) {
	if got := Weekday(2000, 1, 1); got != "Saturday" {
		t.Fatalf("Weekday(2000,1,1) = %q, want Saturday", got)
	}
}
