package runtime

import (
	"sync"
	"testing"
	"time"
)

func TestShutdownIsIdempotentAndRaceFree(t *testing.T) {
	s := NewServer()
	s.Start()

	var wg sync.WaitGroup
	for i := 0; i < 20; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			_ = s.Submit("tick")
		}()
	}
	time.Sleep(10 * time.Millisecond)
	s.Shutdown()
	s.Shutdown()
	wg.Wait()
	_ = s.Handled()
}

func TestSubmitAfterShutdownFails(t *testing.T) {
	s := NewServer()
	s.Start()
	s.Shutdown()
	if s.Submit("late") {
		t.Fatal("submit after shutdown should fail")
	}
}
