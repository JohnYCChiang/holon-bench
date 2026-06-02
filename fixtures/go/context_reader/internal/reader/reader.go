package reader

import "context"

func ReadAll(ctx context.Context, in <-chan string) ([]string, error) {
	var values []string
	for value := range in {
		values = append(values, value)
	}
	return values, ctx.Err()
}
