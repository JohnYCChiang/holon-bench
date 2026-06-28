package fanin

// FanIn merges the values from all input channels into a single output
// channel. Each input is drained by its own goroutine. The output channel is
// closed exactly once after every input channel has been fully drained, and no
// goroutine may leak.
func FanIn(inputs ...<-chan int) <-chan int {
	out := make(chan int)
	for _, in := range inputs {
		go func(c <-chan int) {
			for v := range c {
				out <- v
			}
		}(in)
	}
	close(out)
	return out
}
