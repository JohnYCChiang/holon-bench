package spectate

import "testing"

func TestHandoffToOldestRemaining(t *testing.T) {
	a := NewArena()
	a.AddPlayer("a")
	a.AddPlayer("b")
	if !a.Spectate("s1", "a") {
		t.Fatal("spectate of live player must succeed")
	}
	a.Leave("a")
	if got := a.Target("s1"); got != "b" {
		t.Fatalf("target=%q want b after handoff", got)
	}
}

func TestHandoffIdleWhenNonePresent(t *testing.T) {
	a := NewArena()
	a.AddPlayer("a")
	a.Spectate("s1", "a")
	a.Leave("a")
	if got := a.Target("s1"); got != "" {
		t.Fatalf("target=%q want idle when no players remain", got)
	}
}
