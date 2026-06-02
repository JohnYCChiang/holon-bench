package fanout

func Fanout(in <-chan int, workers int) <-chan int {
	out := make(chan int)
	for i := 0; i < workers; i++ {
		go func() {
			for value := range in {
				out <- value * 2
			}
		}()
	}
	return out
}
