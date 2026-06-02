package worker

import (
	"context"
	"testing"
	"time"
)

func TestHiddenWorkerStillProcessesValuesBeforeCancellation(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	input := make(chan int)
	out := Start(ctx, input)

	input <- 3
	select {
	case got := <-out:
		if got != 6 {
			t.Fatalf("expected doubled value 6, got %d", got)
		}
	case <-time.After(200 * time.Millisecond):
		t.Fatal("worker did not produce output before cancellation")
	}

	cancel()
	select {
	case _, ok := <-out:
		if ok {
			t.Fatal("output should close after cancellation")
		}
	case <-time.After(200 * time.Millisecond):
		t.Fatal("worker did not close output after cancellation")
	}
}

func TestHiddenWorkerClosesOutputWhenInputCloses(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	input := make(chan int)
	out := Start(ctx, input)
	close(input)

	select {
	case _, ok := <-out:
		if ok {
			t.Fatal("output should close when input closes")
		}
	case <-time.After(200 * time.Millisecond):
		t.Fatal("worker did not close output after input closed")
	}
}
