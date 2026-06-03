package match

import "testing"

func TestMutationCancelRemovesAllQueuedEntriesForPlayer(t *testing.T) {
	var q Queue
	q.Enqueue("a")
	q.Enqueue("b")
	q.Enqueue("a")
	q.Enqueue("c")
	q.Cancel("a")

	got := q.Match(2)
	want := []string{"b", "c"}
	if len(got) != len(want) {
		t.Fatalf("match length = %d, want %d: %#v", len(got), len(want), got)
	}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("match = %#v, want %#v", got, want)
		}
	}
}
