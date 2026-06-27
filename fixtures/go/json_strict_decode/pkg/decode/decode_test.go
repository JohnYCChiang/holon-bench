package decode

import (
	"errors"
	"testing"
)

func TestDecodeKnownFields(t *testing.T) {
	s, err := Decode([]byte(`{"name":"svc","timeout":30}`))
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if s.Name != "svc" || s.Timeout != 30 {
		t.Fatalf("decoded = %#v", s)
	}
}

func TestDecodeRejectsUnknownField(t *testing.T) {
	_, err := Decode([]byte(`{"name":"svc","extra":true}`))
	if !errors.Is(err, ErrUnknownField) {
		t.Fatalf("expected ErrUnknownField, got %v", err)
	}
}
