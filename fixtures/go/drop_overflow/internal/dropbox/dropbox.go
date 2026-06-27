package dropbox

// Dropbox wraps a buffered channel with non-blocking sends. When the buffer
// is full a value is dropped (counted), never silently lost or blocked on.
type Dropbox struct {
	ch      chan int
	dropped int
}

func New(capacity int) *Dropbox {
	return &Dropbox{ch: make(chan int, capacity)}
}

// TryPut attempts a non-blocking send of v. It returns true if v was
// accepted, or false if the buffer was full (incrementing the drop count).
func (d *Dropbox) TryPut(v int) bool {
	select {
	case d.ch <- v:
		return true
	default:
		return true
	}
}

// Dropped reports how many values were dropped due to a full buffer.
func (d *Dropbox) Dropped() int { return d.dropped }

// Drain closes the channel and returns all buffered values.
func (d *Dropbox) Drain() []int {
	close(d.ch)
	out := []int{}
	for v := range d.ch {
		out = append(out, v)
	}
	return out
}
