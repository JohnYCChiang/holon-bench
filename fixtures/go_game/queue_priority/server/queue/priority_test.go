package queue

import "testing"

func TestTieIsFIFO(t *testing.T) {
	q := NewPQueue()
	q.Push("a", 5)
	q.Push("b", 5)
	id, ok := q.Pop()
	if !ok || id != "a" {
		t.Fatalf("pop=%q ok=%v want a (FIFO tie)", id, ok)
	}
}

func TestHighestPriorityFirst(t *testing.T) {
	q := NewPQueue()
	q.Push("low", 1)
	q.Push("high", 9)
	id, _ := q.Pop()
	if id != "high" {
		t.Fatalf("pop=%q want high", id)
	}
}
