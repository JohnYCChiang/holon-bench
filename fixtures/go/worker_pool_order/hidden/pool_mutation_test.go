package pool

import (
	"testing"
	"time"
)

func TestMutationZeroWorkersStillProcessesJobsWithoutDeadlock(t *testing.T) {
	jobs := []Job{{ID: 1, Value: 2}, {ID: 2, Value: 3}}
	done := make(chan []Result, 1)
	go func() {
		done <- Process(jobs, 0)
	}()

	select {
	case got := <-done:
		want := []Result{{ID: 1, Value: 4}, {ID: 2, Value: 6}}
		for i := range want {
			if got[i] != want[i] {
				t.Fatalf("got %v, want %v", got, want)
			}
		}
	case <-time.After(250 * time.Millisecond):
		t.Fatal("zero-worker configuration deadlocked")
	}
}
