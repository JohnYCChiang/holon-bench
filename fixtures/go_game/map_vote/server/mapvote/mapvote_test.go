package mapvote

import "testing"

func TestTieBrokenBySmallestID(t *testing.T) {
	p := NewPoll([]string{"zebra", "alpha"})
	p.Cast("p1", "zebra")
	p.Cast("p2", "alpha")
	if got := p.Winner(); got != "alpha" {
		t.Fatalf("tie winner=%q want alpha", got)
	}
}

func TestRejectsInvalidOption(t *testing.T) {
	p := NewPoll([]string{"a"})
	if p.Cast("p1", "ghost") {
		t.Fatal("vote for unregistered map must be rejected")
	}
	if p.Winner() != "" {
		t.Fatal("no valid votes means no winner")
	}
}
