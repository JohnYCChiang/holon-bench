package parse

import (
	"errors"
	"testing"
	"time"
)

func TestDurationTable(t *testing.T) {
	tests := []struct {
		name    string
		input   string
		want    time.Duration
		wantErr bool
	}{
		{name: "seconds", input: "2s", want: 2 * time.Second},
		{name: "milliseconds", input: "250ms", want: 250 * time.Millisecond},
		{name: "negative", input: "-1s", wantErr: true},
		{name: "missing suffix", input: "12", wantErr: true},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := Duration(tt.input)
			if tt.wantErr {
				if !errors.Is(err, ErrInvalidDuration) {
					t.Fatalf("expected ErrInvalidDuration, got %v", err)
				}
				return
			}
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tt.want {
				t.Fatalf("got %v want %v", got, tt.want)
			}
		})
	}
}
