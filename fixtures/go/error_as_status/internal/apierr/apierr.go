package apierr

import "fmt"

// HTTPError carries an HTTP status code through the error chain.
type HTTPError struct {
	Code int
	Msg  string
}

func (e *HTTPError) Error() string {
	return fmt.Sprintf("http %d: %s", e.Code, e.Msg)
}

// StatusCode returns the HTTP status code carried by err or by any error it
// wraps. It returns 200 when err is nil and 500 when no *HTTPError is present
// anywhere in the chain.
func StatusCode(err error) int {
	if err == nil {
		return 200
	}
	if he, ok := err.(*HTTPError); ok {
		return he.Code
	}
	return 500
}
