package pool

import "testing"

func TestProcessPreservesInputOrder(t *testing.T) {
	jobs := []Job{{ID: 1, Value: 2}, {ID: 2, Value: 3}, {ID: 3, Value: 4}}
	got := Process(jobs, 2)
	want := []Result{{ID: 1, Value: 4}, {ID: 2, Value: 6}, {ID: 3, Value: 8}}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("got %v want %v", got, want)
		}
	}
}
