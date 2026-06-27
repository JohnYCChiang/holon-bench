package guard

import (
	"errors"
	"strings"
	"testing"
)

func TestGuardPassesThroughNil(t *testing.T) {
	if err := Guard(func() error { return nil }); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestGuardPassesThroughError(t *testing.T) {
	sentinel := errors.New("boom")
	err := Guard(func() error { return sentinel })
	if !errors.Is(err, sentinel) {
		t.Fatalf("expected sentinel, got %v", err)
	}
	if errors.Is(err, ErrPanic) {
		t.Fatalf("normal error must not be wrapped as ErrPanic")
	}
}

func TestGuardRecoversPanic(t *testing.T) {
	err := Guard(func() error { panic("kaboom") })
	if !errors.Is(err, ErrPanic) {
		t.Fatalf("expected ErrPanic, got %v", err)
	}
	if !strings.Contains(err.Error(), "kaboom") {
		t.Fatalf("expected panic value in error, got %q", err.Error())
	}
}
