package loader

import (
	"errors"
	"io/fs"
	"strings"
	"testing"
)

func TestLoadConfigWrapsReadErrors(t *testing.T) {
	_, err := LoadConfig("missing.json", func(string) ([]byte, error) {
		return nil, fs.ErrNotExist
	})
	if err == nil {
		t.Fatal("expected error")
	}
	if !errors.Is(err, fs.ErrNotExist) {
		t.Fatalf("expected wrapped fs.ErrNotExist, got %v", err)
	}
	if !strings.Contains(err.Error(), "missing.json") {
		t.Fatalf("expected path context in error, got %q", err.Error())
	}
}

func TestLoadConfigInvalidInputUsesSentinel(t *testing.T) {
	tests := []struct {
		name string
		path string
		data []byte
	}{
		{name: "empty path", path: "", data: []byte(`{"name":"ok"}`)},
		{name: "bad json", path: "bad.json", data: []byte(`{`)},
		{name: "missing name", path: "missing-name.json", data: []byte(`{"name":""}`)},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			_, err := LoadConfig(tc.path, func(string) ([]byte, error) {
				return tc.data, nil
			})
			if !errors.Is(err, ErrInvalidConfig) {
				t.Fatalf("expected ErrInvalidConfig, got %v", err)
			}
		})
	}
}

func TestLoadConfigSuccess(t *testing.T) {
	cfg, err := LoadConfig("ok.json", func(string) ([]byte, error) {
		return []byte(`{"name":"demo"}`), nil
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if cfg.Name != "demo" {
		t.Fatalf("unexpected config: %#v", cfg)
	}
}
