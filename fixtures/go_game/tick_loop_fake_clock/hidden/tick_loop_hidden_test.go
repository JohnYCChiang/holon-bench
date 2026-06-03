package tick

import (
	"context"
	"sync/atomic"
	"testing"
	"time"
)

func TestHiddenRunWithTicksReturnsWhenTickSourceCloses(t *testing.T) {
	ticks := make(chan time.Time)
	close(ticks)

	var count atomic.Int32
	done := make(chan struct{})
	loop := Loop{
		Interval: time.Hour,
		Step: func() {
			count.Add(1)
		},
	}

	go func() {
		defer close(done)
		loop.RunWithTicks(context.Background(), ticks)
	}()

	select {
	case <-done:
	case <-time.After(200 * time.Millisecond):
		t.Fatal("RunWithTicks did not return after the tick source closed")
	}

	if got := count.Load(); got != 0 {
		t.Fatalf("Step called %d times after tick source closed, want 0", got)
	}
}
