package backoff

import "testing"

func TestDelayIsCapped(t *testing.T) {
	b := New(100, 1000)
	if got := b.Delay(5); got != 1000 {
		t.Fatalf("Delay(5) = %d, want 1000 (capped)", got)
	}
}
