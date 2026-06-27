package retry

import (
	"errors"
	"testing"
)

func TestSucceedsOnLastAttempt(t *testing.T) {
	calls := 0
	err := Do(3, func() error {
		calls++
		if calls < 3 {
			return errors.New("transient")
		}
		return nil
	})
	if err != nil {
		t.Fatalf("expected success, got %v", err)
	}
	if calls != 3 {
		t.Fatalf("expected 3 calls, got %d", calls)
	}
}
