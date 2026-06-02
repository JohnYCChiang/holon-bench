package config

import (
	"errors"
	"testing"
)

func TestNewRejectsInvalidConfig(t *testing.T) {
	if _, err := New("", 8080); !errors.Is(err, ErrInvalidConfig) {
		t.Fatalf("expected invalid config for empty host, got %v", err)
	}
	if _, err := New("localhost", 0); !errors.Is(err, ErrInvalidConfig) {
		t.Fatalf("expected invalid config for invalid port, got %v", err)
	}
}

func TestConfigAccessors(t *testing.T) {
	cfg, err := New("localhost", 8080)
	if err != nil {
		t.Fatalf("New returned error: %v", err)
	}
	if cfg.Hostname() != "localhost" || cfg.PortNumber() != 8080 {
		t.Fatalf("unexpected config values: %#v", cfg)
	}
}
