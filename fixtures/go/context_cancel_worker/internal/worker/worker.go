package worker

import "context"

func Start(ctx context.Context, input <-chan int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for v := range input {
			out <- v * 2
			_ = ctx
		}
	}()
	return out
}
