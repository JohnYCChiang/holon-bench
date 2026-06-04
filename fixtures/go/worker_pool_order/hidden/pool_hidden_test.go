package pool

import "testing"

func TestHiddenEmptyJobsReturnEmptyResults(t *testing.T) {
	got := Process(nil, 0)
	if len(got) != 0 {
		t.Fatalf("got %v, want empty results", got)
	}
}
