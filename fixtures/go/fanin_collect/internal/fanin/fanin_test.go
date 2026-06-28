package fanin

import (
	"sort"
	"testing"
)

// chanOf returns a buffered channel pre-loaded with vs and already closed.
func chanOf(vs ...int) <-chan int {
	ch := make(chan int, len(vs))
	for _, v := range vs {
		ch <- v
	}
	close(ch)
	return ch
}

// drain collects all values from ch into a sorted slice.
func drain(ch <-chan int) []int {
	out := []int{}
	for v := range ch {
		out = append(out, v)
	}
	sort.Ints(out)
	return out
}

func TestFanInCollectsAllValues(t *testing.T) {
	got := drain(FanIn(chanOf(1, 2, 3), chanOf(4, 5, 6)))
	want := []int{1, 2, 3, 4, 5, 6}
	if len(got) != len(want) {
		t.Fatalf("got %d values, want %d: %v", len(got), len(want), got)
	}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("FanIn values = %v, want %v", got, want)
		}
	}
}
