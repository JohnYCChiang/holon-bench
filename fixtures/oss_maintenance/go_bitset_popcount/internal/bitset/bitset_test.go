package bitset

import "testing"

func TestPopCountHighBit(t *testing.T) {
	if got := PopCount(1 << 40); got != 1 {
		t.Fatalf("PopCount(1<<40) = %d, want 1", got)
	}
}
