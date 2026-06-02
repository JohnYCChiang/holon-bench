package bus

type Bus struct {
	done chan struct{}
}

func New() *Bus {
	return &Bus{done: make(chan struct{})}
}

func (b *Bus) Done() <-chan struct{} {
	return b.done
}

func (b *Bus) Close() {
	close(b.done)
}
