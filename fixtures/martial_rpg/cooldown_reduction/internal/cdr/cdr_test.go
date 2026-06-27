package cdr

import "testing"

func TestAdditiveStack(t *testing.T) {
	// 10% + 20% = 30% off 100 -> 70
	if got := Effective(100, []int{10, 20}, 40, 0); got != 70 {
		t.Fatalf("cooldown = %d, want 70", got)
	}
}

func TestCappedAtMaxCDR(t *testing.T) {
	// 30 + 30 = 60 capped to 40 -> 60
	if got := Effective(100, []int{30, 30}, 40, 0); got != 60 {
		t.Fatalf("cooldown = %d, want 60", got)
	}
}

func TestIntegerFloor(t *testing.T) {
	// 33% off 100 -> 67
	if got := Effective(100, []int{33}, 80, 0); got != 67 {
		t.Fatalf("cooldown = %d, want 67", got)
	}
}
