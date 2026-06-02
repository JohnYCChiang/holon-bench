package queue

import (
	"context"
	"testing"
	"time"
)

func TestHiddenBlockedEnqueueCompletesAfterDequeue(t *testing.T) {
	q := New(1)
	if err := q.Enqueue(context.Background(), "first"); err != nil {
		t.Fatalf("unexpected first enqueue error: %v", err)
	}

	done := make(chan error, 1)
	go func() {
		done <- q.Enqueue(context.Background(), "second")
	}()

	select {
	case err := <-done:
		t.Fatalf("enqueue completed while queue was still full: %v", err)
	case <-time.After(20 * time.Millisecond):
	}

	got, err := q.Dequeue(context.Background())
	if err != nil {
		t.Fatalf("unexpected dequeue error: %v", err)
	}
	if got != "first" {
		t.Fatalf("first dequeue should preserve existing message, got %q", got)
	}

	select {
	case err := <-done:
		if err != nil {
			t.Fatalf("blocked enqueue should succeed after space is available: %v", err)
		}
	case <-time.After(200 * time.Millisecond):
		t.Fatal("blocked enqueue did not resume after dequeue")
	}

	got, err = q.Dequeue(context.Background())
	if err != nil {
		t.Fatalf("unexpected second dequeue error: %v", err)
	}
	if got != "second" {
		t.Fatalf("second dequeue should return unblocked message, got %q", got)
	}
}

func TestHiddenZeroBufferHonorsContextCancellation(t *testing.T) {
	q := New(0)
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Millisecond)
	defer cancel()

	started := time.Now()
	err := q.Enqueue(ctx, "never")
	if err == nil {
		t.Fatal("enqueue on zero-buffer queue without receiver should return context error")
	}
	if time.Since(started) > 200*time.Millisecond {
		t.Fatal("enqueue ignored context cancellation for too long")
	}
}
