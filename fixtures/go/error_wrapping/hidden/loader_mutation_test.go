package loader

import (
	"errors"
	"strings"
	"testing"
)

func TestMutationInvalidConfigVariantsKeepSentinelAndContext(t *testing.T) {
	tests := []struct {
		name string
		path string
		data []byte
	}{
		{name: "wrong name type", path: "wrong-type.json", data: []byte(`{"name":42}`)},
		{name: "null name", path: "null-name.json", data: []byte(`{"name":null}`)},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			_, err := LoadConfig(tc.path, func(string) ([]byte, error) {
				return tc.data, nil
			})
			if !errors.Is(err, ErrInvalidConfig) {
				t.Fatalf("expected ErrInvalidConfig, got %v", err)
			}
			if err == ErrInvalidConfig {
				t.Fatalf("expected path context wrapping, got bare sentinel")
			}
			if !strings.Contains(err.Error(), tc.path) {
				t.Fatalf("expected path context in error, got %q", err.Error())
			}
		})
	}
}
