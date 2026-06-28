package chat

import "testing"

func TestBurstThenDrop(t *testing.T) {
	f := NewFilter(3, 100)
	for i := 0; i < 3; i++ {
		if !f.Allow("a", 0) {
			t.Fatalf("message %d should be allowed", i)
		}
	}
	if f.Allow("a", 0) {
		t.Fatal("4th message in window must be dropped")
	}
}

func TestWindowResetsAllowsAgain(t *testing.T) {
	f := NewFilter(2, 100)
	f.Allow("a", 0)
	f.Allow("a", 0)
	if f.Allow("a", 50) {
		t.Fatal("still inside window, must drop")
	}
	if !f.Allow("a", 101) {
		t.Fatal("window passed, message must be allowed again")
	}
}
