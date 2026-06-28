package match

import (
	"reflect"
	"sort"
	"testing"
)

func sample() []Player {
	return []Player{
		{"alice", 30}, {"bob", 10}, {"carol", 25}, {"dave", 5},
		{"erin", 20}, {"frank", 15},
	}
}

func TestBalanceDeterministicAcrossInputOrder(t *testing.T) {
	a := BalanceTeams(sample())
	rev := sample()
	for i, j := 0, len(rev)-1; i < j; i, j = i+1, j-1 {
		rev[i], rev[j] = rev[j], rev[i]
	}
	b := BalanceTeams(rev)
	if !reflect.DeepEqual(a, b) {
		t.Fatalf("teams depend on input order:\n a=%v\n b=%v", a, b)
	}
}

func TestBalanceSortedAndEvenSizes(t *testing.T) {
	out := BalanceTeams(sample())
	if !sort.StringsAreSorted(out.A) || !sort.StringsAreSorted(out.B) {
		t.Fatalf("team lists not sorted: %v", out)
	}
	if d := len(out.A) - len(out.B); d < -1 || d > 1 {
		t.Fatalf("team sizes off by more than 1: %v", out)
	}
}
