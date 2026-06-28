package skipvote

import "testing"

func TestExactThresholdPasses(t *testing.T) {
	s := NewSkip(2, 3) // two-thirds supermajority
	s.Join("a")
	s.Join("b")
	s.Join("c")
	s.Vote("a")
	s.Vote("b")
	if !s.Passed() { // 2 of 3 votes == exactly two-thirds
		t.Fatal("an exactly-at-threshold supermajority must pass")
	}
}

func TestBelowThresholdFails(t *testing.T) {
	s := NewSkip(2, 3)
	s.Join("a")
	s.Join("b")
	s.Join("c")
	s.Vote("a")
	if s.Passed() { // 1 of 3 < two-thirds
		t.Fatal("a single vote must not pass a supermajority")
	}
}
