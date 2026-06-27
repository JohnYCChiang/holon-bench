package retry

import (
	"context"
	"errors"
	"testing"
	"time"
)

func TestCancelReturnsContextError(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	err := Retry(ctx, time.Millisecond, func() error { return errors.New("always") })
	if !errors.Is(err, context.Canceled) {
		t.Fatalf("expected context.Canceled, got %v", err)
	}
}

func TestCancelStopsOnSuccess(t *testing.T) {
	calls := 0
	err := Retry(context.Background(), time.Millisecond, func() error {
		calls++
		if calls < 3 {
			return errors.New("not yet")
		}
		return nil
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if calls != 3 {
		t.Fatalf("fn called %d times, want 3", calls)
	}
}
