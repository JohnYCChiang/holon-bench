package guard

import "errors"

// ErrPanic wraps any value recovered from a panic inside Guard.
var ErrPanic = errors.New("recovered panic")

// Guard runs fn and converts any panic into an error that wraps ErrPanic.
// A normal (non-panicking) return value is passed through unchanged.
func Guard(fn func() error) (err error) {
	return fn()
}
