package room

import "testing"

func TestKicksOnStrictMajority(t *testing.T) {
	v := &VoteSession{Voters: 5, Target: "bad"}
	if v.Vote("a") {
		t.Fatal("1/5 not majority")
	}
	if v.Vote("b") {
		t.Fatal("2/5 not majority")
	}
	if !v.Vote("c") {
		t.Fatal("3/5 is majority -> kick")
	}
}

func TestDuplicateVoteIdempotent(t *testing.T) {
	v := &VoteSession{Voters: 5}
	v.Vote("a")
	if v.Vote("a") {
		t.Fatal("same voter twice must not reach majority")
	}
}
