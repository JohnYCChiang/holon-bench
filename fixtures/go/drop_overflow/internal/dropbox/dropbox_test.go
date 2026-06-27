package dropbox

import (
	"reflect"
	"testing"
)

func TestTryPutDropsWhenFull(t *testing.T) {
	d := New(2)
	if !d.TryPut(1) || !d.TryPut(2) {
		t.Fatal("first two puts should be accepted")
	}
	if d.TryPut(3) {
		t.Fatal("third put should be dropped (returns false)")
	}
	if d.Dropped() != 1 {
		t.Fatalf("Dropped() = %d, want 1", d.Dropped())
	}
	if got := d.Drain(); !reflect.DeepEqual(got, []int{1, 2}) {
		t.Fatalf("Drain() = %v, want [1 2]", got)
	}
}
