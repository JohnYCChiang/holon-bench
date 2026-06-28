package lifo

import (
	"reflect"
	"testing"
)

func TestShutdownReverseOrder(t *testing.T) {
	got := Shutdown([]string{"a", "b", "c"})
	want := []string{"c", "b", "a"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("Shutdown() = %v, want %v", got, want)
	}
}

func TestShutdownEmpty(t *testing.T) {
	got := Shutdown(nil)
	if len(got) != 0 {
		t.Fatalf("Shutdown(nil) = %v, want empty", got)
	}
}
