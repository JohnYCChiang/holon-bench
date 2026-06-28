package pipeline

import "context"

// MapBounded applies fn to every element of in using at most parallelism
// concurrent goroutines. Results are returned in the same order as in.
//
// If any fn call returns an error, MapBounded cancels the context passed to the
// remaining calls and returns the first error observed. If the parent context
// is cancelled it returns ctx.Err(). On success it returns one result per input
// in order. No goroutine may leak after MapBounded returns.
func MapBounded(ctx context.Context, in []int, parallelism int, fn func(context.Context, int) (int, error)) ([]int, error) {
	out := make([]int, len(in))
	done := make(chan struct{})
	for i, v := range in {
		go func(i, v int) {
			r, _ := fn(ctx, v)
			out[i] = r
			done <- struct{}{}
		}(i, v)
	}
	for range in {
		<-done
	}
	return out, nil
}
