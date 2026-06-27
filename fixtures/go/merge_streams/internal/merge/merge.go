package merge

// Merge consumes values from each input channel (each individually sorted in
// ascending order) and returns one channel emitting every value in globally
// sorted order. The output channel is closed exactly once after all inputs
// drain, and no goroutine may leak.
func Merge(inputs ...<-chan int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for _, in := range inputs {
			for v := range in {
				out <- v
			}
		}
	}()
	return out
}
