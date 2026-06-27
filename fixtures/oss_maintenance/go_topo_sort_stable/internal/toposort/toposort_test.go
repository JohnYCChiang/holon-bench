package toposort

import (
	"reflect"
	"testing"
)

func TestStableTieBreak(t *testing.T) {
	got, err := Sort([]string{"b", "a"}, nil)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	want := []string{"b", "a"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("Sort = %v, want %v", got, want)
	}
}
