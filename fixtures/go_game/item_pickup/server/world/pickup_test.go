package world

import "testing"

func TestFirstClaimWins(t *testing.T) {
	it := &Item{ID: "sword"}
	if !it.Claim("a") {
		t.Fatal("first claim should succeed")
	}
	if it.Claim("b") {
		t.Fatal("second claim should fail")
	}
	if it.OwnerID != "a" {
		t.Fatalf("Owner=%q want a", it.OwnerID)
	}
}

func TestEmptyClaimRejected(t *testing.T) {
	it := &Item{ID: "shield"}
	if it.Claim("") {
		t.Fatal("empty player must be rejected")
	}
	if it.OwnerID != "" {
		t.Fatalf("Owner=%q want empty", it.OwnerID)
	}
}
