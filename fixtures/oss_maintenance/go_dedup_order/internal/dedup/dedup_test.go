package dedup

import (
	"reflect"
	"testing"
)

func TestNonConsecutiveDuplicateRemoved(t *testing.T) {
	got := Dedup([]string{"a", "b", "a", "c", "b"})
	want := []string{"a", "b", "c"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("Dedup = %v, want %v", got, want)
	}
}
