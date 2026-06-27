package netio

import "testing"

func TestAcceptsUpToMaxPerTick(t *testing.T) {
	l := &Limiter{Max: 2}
	if !l.Accept("a", 1) || !l.Accept("a", 1) {
		t.Fatal("first two should be accepted")
	}
	if l.Accept("a", 1) {
		t.Fatal("third in same tick should be dropped")
	}
	if l.Dropped != 1 {
		t.Fatalf("Dropped=%d want 1", l.Dropped)
	}
	if !l.Accept("a", 2) {
		t.Fatal("new tick resets the budget")
	}
}
