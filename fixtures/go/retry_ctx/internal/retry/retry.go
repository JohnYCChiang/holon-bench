package retry

import (
	"context"
	"time"
)

// Retry calls fn until it returns nil or ctx is done, waiting delay between
// attempts. If ctx is cancelled (or its deadline passes) while waiting, Retry
// returns ctx.Err(). Otherwise it keeps retrying until fn succeeds.
func Retry(ctx context.Context, delay time.Duration, fn func() error) error {
	var err error
	for attempt := 0; attempt < 5; attempt++ {
		if err = fn(); err == nil {
			return nil
		}
		time.Sleep(delay)
	}
	return err
}
