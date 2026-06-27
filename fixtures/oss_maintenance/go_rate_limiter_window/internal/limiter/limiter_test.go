package limiter

import "testing"

func TestExpiresAtWindowEdge(t *testing.T) {
	l := New(2, 10)
	if !l.Allow(0) {
		t.Fatal("t=0 should be allowed")
	}
	if !l.Allow(1) {
		t.Fatal("t=1 should be allowed")
	}
	if l.Allow(2) {
		t.Fatal("t=2 should be denied (capacity full)")
	}
	if !l.Allow(10) {
		t.Fatal("t=10 should be allowed: event at t=0 has expired")
	}
}
