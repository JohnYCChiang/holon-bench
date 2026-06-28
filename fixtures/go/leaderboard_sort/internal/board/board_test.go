package board

import (
	"reflect"
	"testing"
)

func TestRankByTierThenScoreThenName(t *testing.T) {
	in := []Player{
		{Name: "alice", Tier: "gold", Score: 50},
		{Name: "bob", Tier: "bronze", Score: 10},
		{Name: "carol", Tier: "bronze", Score: 30},
	}
	got := Rank(in)
	want := []Player{
		{Name: "carol", Tier: "bronze", Score: 30},
		{Name: "bob", Tier: "bronze", Score: 10},
		{Name: "alice", Tier: "gold", Score: 50},
	}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("Rank() = %v, want %v", got, want)
	}
}

func TestRankDoesNotMutateInput(t *testing.T) {
	in := []Player{
		{Name: "z", Tier: "silver", Score: 1},
		{Name: "a", Tier: "bronze", Score: 9},
	}
	_ = Rank(in)
	if in[0].Name != "z" || in[1].Name != "a" {
		t.Fatalf("input mutated: %v", in)
	}
}
