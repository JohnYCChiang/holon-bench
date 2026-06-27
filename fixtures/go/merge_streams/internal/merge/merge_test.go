package merge

import "testing"

// chanOf returns a buffered channel pre-loaded with vs and already closed.
func chanOf(vs ...int) <-chan int {
	ch := make(chan int, len(vs))
	for _, v := range vs {
		ch <- v
	}
	close(ch)
	return ch
}

func collect(ch <-chan int) []int {
	out := []int{}
	for v := range ch {
		out = append(out, v)
	}
	return out
}

func sortedCheck(t *testing.T, got []int) {
	t.Helper()
	for i := 1; i < len(got); i++ {
		if got[i-1] > got[i] {
			t.Fatalf("output not sorted at %d: %v", i, got)
		}
	}
}

func TestMergeTwoSorted(t *testing.T) {
	got := collect(Merge(chanOf(1, 3, 5), chanOf(2, 4, 6)))
	sortedCheck(t, got)
	if len(got) != 6 {
		t.Fatalf("got %d values, want 6: %v", len(got), got)
	}
}
