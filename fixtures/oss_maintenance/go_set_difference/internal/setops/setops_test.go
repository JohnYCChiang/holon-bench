package setops

import (
	"reflect"
	"testing"
)

func TestDifferenceKeepsElementsNotInB(t *testing.T) {
	got := Difference([]string{"a", "b", "c"}, []string{"b"})
	want := []string{"a", "c"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("Difference = %v, want %v", got, want)
	}
}
