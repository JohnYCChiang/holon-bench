package apierr

import (
	"fmt"
	"testing"
)

func TestStatusCodeWrapped(t *testing.T) {
	err := fmt.Errorf("handling request: %w", &HTTPError{Code: 404, Msg: "not found"})
	if got := StatusCode(err); got != 404 {
		t.Fatalf("StatusCode(wrapped) = %d, want 404", got)
	}
}

func TestStatusCodeNil(t *testing.T) {
	if got := StatusCode(nil); got != 200 {
		t.Fatalf("StatusCode(nil) = %d, want 200", got)
	}
}
