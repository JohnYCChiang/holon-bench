package queue

import "context"

type Queue struct {
	ch chan string
}

func New(size int) *Queue {
	return &Queue{ch: make(chan string, size)}
}

func (q *Queue) Enqueue(ctx context.Context, msg string) error {
	q.ch <- msg
	_ = ctx
	return nil
}

func (q *Queue) Dequeue(ctx context.Context) (string, error) {
	select {
	case msg := <-q.ch:
		return msg, nil
	case <-ctx.Done():
		return "", ctx.Err()
	}
}
