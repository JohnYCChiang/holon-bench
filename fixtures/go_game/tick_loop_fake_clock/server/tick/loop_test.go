package tick

import (
	"context"
	"sync/atomic"
	"testing"
	"time"
)

func TestLoopUsesInjectableTickSource(t *testing.T) {
	ticks := make(chan time.Time, 3)
	ctx, cancel := context.WithCancel(context.Background())
	var count atomic.Int32
	processed := make(chan struct{}, 3)

	loop := Loop{
		Interval: time.Hour,
		Step: func() {
			count.Add(1)
			processed <- struct{}{}
		},
	}
	go loop.RunWithTicks(ctx, ticks)

	ticks <- time.Unix(1, 0)
	ticks <- time.Unix(2, 0)
	for i := 0; i < 2; i++ {
		select {
		case <-processed:
		case <-time.After(200 * time.Millisecond):
			t.Fatal("loop did not process injected tick")
		}
	}
	cancel()
	ticks <- time.Unix(3, 0)
	time.Sleep(10 * time.Millisecond)

	if got := count.Load(); got != 2 {
		t.Fatalf("tick count = %d, want 2", got)
	}
}

func TestRunStopsOnShutdown(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	done := make(chan struct{})
	loop := Loop{Interval: time.Hour, Step: func() {}}
	go func() {
		defer close(done)
		loop.RunWithTicks(ctx, make(chan time.Time))
	}()
	cancel()
	select {
	case <-done:
	case <-time.After(200 * time.Millisecond):
		t.Fatal("loop did not stop on context cancellation")
	}
}
