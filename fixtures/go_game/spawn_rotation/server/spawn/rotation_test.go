package spawn

import (
	"reflect"
	"testing"
)

func TestAssignDeterministicAcrossOrder(t *testing.T) {
	r1 := NewRotator(4)
	r2 := NewRotator(4)
	a := r1.Assign([]string{"p1", "p2", "p3"})
	b := r2.Assign([]string{"p3", "p1", "p2"})
	if !reflect.DeepEqual(a, b) {
		t.Fatalf("assignment depends on input order: %v vs %v", a, b)
	}
}

func TestAssignUniqueWithinWave(t *testing.T) {
	r := NewRotator(4)
	out := r.Assign([]string{"a", "b", "c", "d"})
	seen := map[int]bool{}
	for _, idx := range out {
		if idx < 0 || idx >= 4 {
			t.Fatalf("index out of range: %d", idx)
		}
		if seen[idx] {
			t.Fatalf("two players share spawn %d: %v", idx, out)
		}
		seen[idx] = true
	}
}
