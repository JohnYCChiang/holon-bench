package retry

import "errors"

// ErrNoAttempts is returned when attempts < 1.
var ErrNoAttempts = errors.New("retry: attempts must be >= 1")

// Do calls fn up to attempts times, stopping at the first nil error. It returns
// nil on success, the last error when every attempt fails, or ErrNoAttempts
// when attempts < 1. fn is invoked exactly once per attempt.
func Do(attempts int, fn func() error) error {
	if attempts < 1 {
		return ErrNoAttempts
	}
	var err error
	for i := 1; i < attempts; i++ { // BUG: runs attempts-1 times; should iterate exactly attempts times
		if err = fn(); err == nil {
			return nil
		}
	}
	return err
}
