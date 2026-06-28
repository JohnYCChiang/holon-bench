package metrics

import (
	"sync"
	"testing"
)

func TestCounterConcurrentInc(t *testing.T) {
	var c Counter
	var wg sync.WaitGroup
	const n = 500
	for i := 0; i < n; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			c.Inc()
		}()
	}
	wg.Wait()
	if got := c.Value(); got != n {
		t.Fatalf("Value() = %d, want %d", got, n)
	}
}
