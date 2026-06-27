package registry

import (
	"reflect"
	"testing"
)

func TestReAddIsNoOp(t *testing.T) {
	s := New()
	s.Add("a")
	s.Add("b")
	s.Add("a") // already present: must be a no-op
	if got := s.Items(); !reflect.DeepEqual(got, []string{"a", "b"}) {
		t.Fatalf("Items() = %v, want [a b]", got)
	}
}
