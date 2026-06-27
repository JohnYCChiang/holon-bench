package worker

import (
	"context"
	"runtime"
	"testing"
	"time"
)

// settleGoroutines waits up to d for the live goroutine count to fall back to
// at most target, nudging the scheduler/GC so a properly-exiting producer is
// observed deterministically.
func settleGoroutines(target int, d time.Duration) int {
	deadline := time.Now().Add(d)
	for time.Now().Before(deadline) {
		runtime.GC()
		if runtime.NumGoroutine() <= target {
			return runtime.NumGoroutine()
		}
		time.Sleep(5 * time.Millisecond)
	}
	return runtime.NumGoroutine()
}

func TestStreamNoLeakOnCancel(t *testing.T) {
	base := runtime.NumGoroutine()
	ctx, cancel := context.WithCancel(context.Background())
	ch := Stream(ctx, 1_000_000)
	if got := <-ch; got != 0 {
		t.Fatalf("first value = %d, want 0", got)
	}
	cancel() // caller stops reading
	if got := settleGoroutines(base, time.Second); got > base {
		t.Fatalf("producer goroutine leaked after cancel: base=%d, got=%d", base, got)
	}
}
