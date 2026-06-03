package runtime

import (
	"fmt"
	"testing"
	"time"
)

func TestHiddenShutdownDrainsAcceptedEvents(t *testing.T) {
	s := NewServer()
	s.Start()

	accepted := make(map[string]bool)
	deadline := time.Now().Add(2 * time.Second)
	for len(accepted) < 5 && time.Now().Before(deadline) {
		event := fmt.Sprintf("event-%d", len(accepted))
		if s.Submit(event) {
			accepted[event] = true
		}
	}
	if len(accepted) != 5 {
		t.Fatalf("accepted %d events before deadline, want 5", len(accepted))
	}

	s.Shutdown()
	handled := s.Handled()
	if len(handled) != len(accepted) {
		t.Fatalf("handled %d events, want %d: %#v", len(handled), len(accepted), handled)
	}
	for _, event := range handled {
		if !accepted[event] {
			t.Fatalf("handled unexpected event %q; accepted=%#v handled=%#v", event, accepted, handled)
		}
		delete(accepted, event)
	}
	if len(accepted) != 0 {
		t.Fatalf("accepted events were not drained: %#v", accepted)
	}
}
