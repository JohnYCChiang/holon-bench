package loader

import (
	"errors"
	"strings"
	"testing"
)

type hiddenReadError struct {
	path string
}

func (e *hiddenReadError) Error() string {
	return "read failed for " + e.path
}

func TestHiddenLoadConfigPreservesTypedReadError(t *testing.T) {
	source := &hiddenReadError{path: "secret.json"}
	_, err := LoadConfig("secret.json", func(string) ([]byte, error) {
		return nil, source
	})

	var target *hiddenReadError
	if !errors.As(err, &target) {
		t.Fatalf("expected wrapped typed read error, got %v", err)
	}
	if target != source {
		t.Fatalf("errors.As returned wrong error instance")
	}
	if !strings.Contains(err.Error(), "secret.json") {
		t.Fatalf("expected path context in wrapped error, got %q", err.Error())
	}
}

func TestHiddenLoadConfigSuccessReadsExactlyOnce(t *testing.T) {
	calls := 0
	cfg, err := LoadConfig("ok.json", func(path string) ([]byte, error) {
		calls++
		if path != "ok.json" {
			t.Fatalf("unexpected path %q", path)
		}
		return []byte(`{"name":"demo"}`), nil
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if cfg.Name != "demo" {
		t.Fatalf("unexpected config: %#v", cfg)
	}
	if calls != 1 {
		t.Fatalf("reader called %d times, want 1", calls)
	}
}
