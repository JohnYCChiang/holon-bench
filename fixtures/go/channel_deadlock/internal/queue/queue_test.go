package queue

import (
	"context"
	"errors"
	"testing"
	"time"
)

func TestEnqueueReturnsWhenContextCancelsOnFullQueue(t *testing.T) {
	q := New(1)
	if err := q.Enqueue(context.Background(), "first"); err != nil {
		t.Fatalf("unexpected first enqueue error: %v", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Millisecond)
	defer cancel()

	done := make(chan error, 1)
	go func() {
		done <- q.Enqueue(ctx, "second")
	}()

	select {
	case err := <-done:
		if !errors.Is(err, context.DeadlineExceeded) {
			t.Fatalf("expected context deadline, got %v", err)
		}
	case <-time.After(200 * time.Millisecond):
		t.Fatal("enqueue blocked after context cancellation")
	}

	got, err := q.Dequeue(context.Background())
	if err != nil {
		t.Fatalf("unexpected dequeue error: %v", err)
	}
	if got != "first" {
		t.Fatalf("queue should preserve first message, got %q", got)
	}
}
