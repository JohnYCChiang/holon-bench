package validate

import (
	"errors"
	"testing"
)

func TestValidateReturnsAllSentinelErrors(t *testing.T) {
	err := Validate(Request{})

	if !errors.Is(err, ErrMissingName) {
		t.Fatalf("expected missing name sentinel, got %v", err)
	}
	if !errors.Is(err, ErrInvalidLimit) {
		t.Fatalf("expected invalid limit sentinel, got %v", err)
	}
}

func TestValidateAcceptsValidRequest(t *testing.T) {
	if err := Validate(Request{Name: "job", Limit: 3}); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
}
