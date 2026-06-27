package initiative

import "testing"

func ids(cs []Combatant) []int {
	out := make([]int, len(cs))
	for i, c := range cs {
		out[i] = c.ID
	}
	return out
}

func equal(a, b []int) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}

func TestOrdersBySpeedDescending(t *testing.T) {
	got := ids(Order([]Combatant{{ID: 1, Speed: 5}, {ID: 2, Speed: 9}, {ID: 3, Speed: 7}}))
	if !equal(got, []int{2, 3, 1}) {
		t.Fatalf("order = %v, want [2 3 1]", got)
	}
}

func TestTiesBrokenByID(t *testing.T) {
	got := ids(Order([]Combatant{{ID: 3, Speed: 5}, {ID: 1, Speed: 5}, {ID: 2, Speed: 5}}))
	if !equal(got, []int{1, 2, 3}) {
		t.Fatalf("tie order = %v, want [1 2 3]", got)
	}
}

func TestDeterministicAcrossInputOrder(t *testing.T) {
	a := ids(Order([]Combatant{{ID: 3, Speed: 5}, {ID: 1, Speed: 5}, {ID: 2, Speed: 5}}))
	b := ids(Order([]Combatant{{ID: 2, Speed: 5}, {ID: 3, Speed: 5}, {ID: 1, Speed: 5}}))
	if !equal(a, b) {
		t.Fatalf("non-deterministic: %v vs %v", a, b)
	}
}
