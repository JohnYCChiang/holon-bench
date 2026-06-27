package capture

import "testing"

func TestAttackersAdvance(t *testing.T) {
	if got := Advance(CapturePoint{Progress: 50, ClientProgress: 999}, 3, 1, 5); got != 52 {
		t.Fatalf("advance wrong: got %d want 52", got)
	}
}

func TestRateCapsGain(t *testing.T) {
	if got := Advance(CapturePoint{Progress: 50}, 10, 0, 4); got != 54 {
		t.Fatalf("rate not capped: got %d want 54", got)
	}
}

func TestClampedAt100(t *testing.T) {
	if got := Advance(CapturePoint{Progress: 98}, 9, 0, 5); got != 100 {
		t.Fatalf("progress exceeded 100: got %d want 100", got)
	}
}
