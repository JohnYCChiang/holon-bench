package worker

import (
	"context"
	"testing"
	"time"
)

func TestCancelClosesOutputPromptly(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	input := make(chan int)
	out := Start(ctx, input)

	cancel()

	select {
	case _, ok := <-out:
		if ok {
			t.Fatal("output channel should close after cancellation")
		}
	case <-time.After(200 * time.Millisecond):
		t.Fatal("worker did not exit after context cancellation")
	}
}

func TestCancelUnblocksPendingSend(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	input := make(chan int)
	out := Start(ctx, input)

	input <- 21
	cancel()

	select {
	case <-out:
	case <-time.After(200 * time.Millisecond):
		t.Fatal("worker did not release pending output on cancellation")
	}
}
