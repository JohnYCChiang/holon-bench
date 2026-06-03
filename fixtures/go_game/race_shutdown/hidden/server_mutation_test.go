package runtime

import (
	"testing"
	"time"
)

func TestMutationSubmitBeforeStartDoesNotBlock(t *testing.T) {
	s := NewServer()
	done := make(chan bool, 1)
	go func() {
		done <- s.Submit("early")
	}()

	select {
	case accepted := <-done:
		if accepted {
			t.Fatal("submit before start should not accept an event")
		}
	case <-time.After(250 * time.Millisecond):
		t.Fatal("submit before start blocked")
	}

	s.Shutdown()
}
