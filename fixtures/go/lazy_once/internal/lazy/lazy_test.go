package lazy

import (
	"sync"
	"sync/atomic"
	"testing"
)

func TestGetComputesOnceConcurrently(t *testing.T) {
	var calls atomic.Int64
	v := New(func() int {
		calls.Add(1)
		return 7
	})
	var wg sync.WaitGroup
	results := make([]int, 64)
	for i := range results {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			results[i] = v.Get()
		}(i)
	}
	wg.Wait()
	if calls.Load() != 1 {
		t.Fatalf("init called %d times, want 1", calls.Load())
	}
	for i, r := range results {
		if r != 7 {
			t.Fatalf("result[%d] = %d, want 7", i, r)
		}
	}
}
