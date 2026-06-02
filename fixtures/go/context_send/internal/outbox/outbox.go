package outbox

import "context"

type Outbox struct {
	ch chan string
}

func New(size int) *Outbox {
	return &Outbox{ch: make(chan string, size)}
}

func (o *Outbox) Enqueue(ctx context.Context, msg string) error {
	o.ch <- msg
	return ctx.Err()
}

func (o *Outbox) Messages() <-chan string {
	return o.ch
}
