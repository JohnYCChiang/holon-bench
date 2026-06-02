package outbox

import (
	"context"
	"errors"
	"testing"
	"time"
)

func TestEnqueueReturnsWhenContextCanceledOnFullChannel(t *testing.T) {
	box := New(1)
	if err := box.Enqueue(context.Background(), "first"); err != nil {
		t.Fatalf("unexpected enqueue error: %v", err)
	}
	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	done := make(chan error, 1)
	go func() {
		done <- box.Enqueue(ctx, "second")
	}()

	select {
	case err := <-done:
		if !errors.Is(err, context.Canceled) {
			t.Fatalf("expected context canceled, got %v", err)
		}
	case <-time.After(200 * time.Millisecond):
		t.Fatal("enqueue did not return after cancellation")
	}
	if got := <-box.Messages(); got != "first" {
		t.Fatalf("accepted message was dropped: %q", got)
	}
}
