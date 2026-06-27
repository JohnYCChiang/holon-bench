package poise

import "testing"

func TestPartialHitDepletesPoise(t *testing.T) {
	s := ApplyPoiseDamage(PoiseState{Poise: 100, MaxPoise: 100}, Hit{PoiseDamage: 30})
	if s.Poise != 70 {
		t.Fatalf("poise = %d, want 70", s.Poise)
	}
	if s.Staggered {
		t.Fatalf("should not be staggered")
	}
}

func TestBreakStaggersAndRestores(t *testing.T) {
	s := ApplyPoiseDamage(PoiseState{Poise: 20, MaxPoise: 100}, Hit{PoiseDamage: 25})
	if !s.Staggered {
		t.Fatalf("expected stagger on break")
	}
	if s.Poise != 100 {
		t.Fatalf("poise should restore to max, got %d", s.Poise)
	}
}

func TestIgnoresClientStaggerClaim(t *testing.T) {
	s := ApplyPoiseDamage(PoiseState{Poise: 100, MaxPoise: 100}, Hit{PoiseDamage: 5, ClientStaggered: true})
	if s.Staggered {
		t.Fatalf("client stagger claim was trusted")
	}
}
