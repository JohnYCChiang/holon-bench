package match

import "testing"

func TestCancelRemovesPlayerFromQueue(t *testing.T) {
	var q Queue
	q.Enqueue("a")
	q.Enqueue("b")
	q.Enqueue("c")
	q.Cancel("b")

	got := q.Match(2)
	want := []string{"a", "c"}
	if len(got) != len(want) || got[0] != want[0] || got[1] != want[1] {
		t.Fatalf("match = %#v, want %#v", got, want)
	}
}

func TestCancelledPlayerCannotBeMatchedLater(t *testing.T) {
	var q Queue
	q.Enqueue("a")
	q.Enqueue("b")
	q.Cancel("a")
	q.Enqueue("c")

	got := q.Match(2)
	if got[0] != "b" || got[1] != "c" {
		t.Fatalf("match = %#v, want b,c", got)
	}
}
