package rank

import (
	"reflect"
	"testing"
)

func TestRankTieBrokenByName(t *testing.T) {
	in := []Item{
		{Name: "c", Score: 5},
		{Name: "a", Score: 5},
		{Name: "b", Score: 9},
	}
	got := Rank(in)
	want := []Item{
		{Name: "b", Score: 9},
		{Name: "a", Score: 5},
		{Name: "c", Score: 5},
	}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("Rank() = %v, want %v", got, want)
	}
}

func TestRankDoesNotMutateInput(t *testing.T) {
	in := []Item{{Name: "z", Score: 1}, {Name: "a", Score: 1}}
	_ = Rank(in)
	if in[0].Name != "z" || in[1].Name != "a" {
		t.Fatalf("input mutated: %v", in)
	}
}
