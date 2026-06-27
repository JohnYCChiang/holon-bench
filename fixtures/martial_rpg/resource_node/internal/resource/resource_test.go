package resource

import "testing"

func TestHarvestPartial(t *testing.T) {
	n, got := Harvest(Node{Amount: 10, ClientAmount: 999}, 3)
	if got != 3 {
		t.Fatalf("yield = %d, want 3", got)
	}
	if n.Amount != 7 {
		t.Fatalf("amount = %d, want 7", n.Amount)
	}
}

func TestHarvestClampedToStock(t *testing.T) {
	n, got := Harvest(Node{Amount: 5}, 20)
	if got != 5 {
		t.Fatalf("yield = %d, want 5 (clamped to stock)", got)
	}
	if n.Amount != 0 {
		t.Fatalf("amount = %d, want 0", n.Amount)
	}
}

func TestDepletedYieldsNothing(t *testing.T) {
	n, got := Harvest(Node{Amount: 0}, 5)
	if got != 0 || n.Amount != 0 {
		t.Fatalf("depleted node gave yield = %d amount = %d, want 0/0", got, n.Amount)
	}
}
