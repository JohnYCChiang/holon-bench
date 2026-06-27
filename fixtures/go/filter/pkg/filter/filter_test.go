package filter

import (
	"encoding/json"
	"reflect"
	"testing"
)

func TestFilterKeepsMatches(t *testing.T) {
	got := Filter([]int{1, 2, 3, 4}, func(v int) bool { return v%2 == 0 })
	want := []int{2, 4}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("Filter() = %v, want %v", got, want)
	}
}

func TestFilterNoMatchIsEmptyNotNil(t *testing.T) {
	got := Filter([]int{1, 3, 5}, func(v int) bool { return v%2 == 0 })
	if got == nil {
		t.Fatal("expected non-nil empty slice, got nil")
	}
	if len(got) != 0 {
		t.Fatalf("expected empty slice, got %v", got)
	}
	b, _ := json.Marshal(got)
	if string(b) != "[]" {
		t.Fatalf("JSON = %s, want []", b)
	}
}
