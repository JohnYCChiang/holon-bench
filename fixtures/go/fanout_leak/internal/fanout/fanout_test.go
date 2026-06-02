package fanout

import (
	"sort"
	"testing"
	"time"
)

func TestFanoutClosesAfterInputDrained(t *testing.T) {
	in := make(chan int)
	out := Fanout(in, 3)
	go func() {
		defer close(in)
		for _, value := range []int{1, 2, 3, 4} {
			in <- value
		}
	}()

	var got []int
	timeout := time.After(500 * time.Millisecond)
	for {
		select {
		case value, ok := <-out:
			if !ok {
				sort.Ints(got)
				want := []int{2, 4, 6, 8}
				for i := range want {
					if got[i] != want[i] {
						t.Fatalf("got %v want %v", got, want)
					}
				}
				return
			}
			got = append(got, value)
		case <-timeout:
			t.Fatalf("fanout did not close, got %v", got)
		}
	}
}
