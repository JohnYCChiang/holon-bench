package reader

import (
	"context"
	"errors"
	"testing"
	"time"
)

func TestReadAllCancelReturnsPromptly(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	in := make(chan string)
	cancel()

	done := make(chan error, 1)
	go func() {
		_, err := ReadAll(ctx, in)
		done <- err
	}()

	select {
	case err := <-done:
		if !errors.Is(err, context.Canceled) {
			t.Fatalf("expected context canceled, got %v", err)
		}
	case <-time.After(200 * time.Millisecond):
		t.Fatal("ReadAll did not return after cancellation")
	}
}
