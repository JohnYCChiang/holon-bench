package bus

import (
	"sync"
	"testing"
	"time"
)

func TestCloseIsConcurrentSafeAndIdempotent(t *testing.T) {
	b := New()
	var wg sync.WaitGroup
	for i := 0; i < 16; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			b.Close()
		}()
	}
	wg.Wait()

	select {
	case <-b.Done():
	case <-time.After(200 * time.Millisecond):
		t.Fatal("done channel was not closed")
	}
	b.Close()
}
