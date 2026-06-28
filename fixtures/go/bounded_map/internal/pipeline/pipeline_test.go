package pipeline

import (
	"context"
	"errors"
	"testing"
)

func square(_ context.Context, v int) (int, error) { return v * v, nil }

func TestMapBoundedOrderedResults(t *testing.T) {
	in := []int{1, 2, 3, 4, 5, 6}
	got, err := MapBounded(context.Background(), in, 3, square)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	want := []int{1, 4, 9, 16, 25, 36}
	if len(got) != len(want) {
		t.Fatalf("got %v, want %v", got, want)
	}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("got %v, want %v", got, want)
		}
	}
}

func TestMapBoundedReturnsError(t *testing.T) {
	boom := errors.New("boom")
	fn := func(_ context.Context, v int) (int, error) {
		if v == 3 {
			return 0, boom
		}
		return v, nil
	}
	_, err := MapBounded(context.Background(), []int{1, 2, 3, 4}, 2, fn)
	if !errors.Is(err, boom) {
		t.Fatalf("error = %v, want boom", err)
	}
}
