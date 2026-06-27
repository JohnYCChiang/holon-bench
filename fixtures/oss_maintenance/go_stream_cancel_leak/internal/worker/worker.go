package worker

import "context"

// Stream sends 0..n-1 on the returned channel, in order, then closes it.
//
// The caller may stop reading at any time (for example when ctx is cancelled).
// The producer goroutine must not leak when that happens: on cancellation it
// must stop sending and return.
func Stream(ctx context.Context, n int) <-chan int {
	out := make(chan int)
	go func() {
		for i := 0; i < n; i++ {
			out <- i
		}
		close(out)
	}()
	return out
}
