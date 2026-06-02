package tool

import (
	"context"
	"testing"
)

type basicRunner struct{}

func (basicRunner) Run(context.Context, Request) (Result, error) {
	return Result{Output: "basic"}, nil
}

type streamingRunner struct{}

func (streamingRunner) Run(context.Context, Request) (Result, error) {
	return Result{Output: "streaming"}, nil
}

func (streamingRunner) SupportsStreaming() bool {
	return true
}

func TestSupportsStreamingUsesOptionalInterface(t *testing.T) {
	tests := []struct {
		name string
		r    Runner
		want bool
	}{
		{name: "basic implementation remains valid", r: basicRunner{}, want: false},
		{name: "streaming capability discovered", r: streamingRunner{}, want: true},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			if got := SupportsStreaming(tc.r); got != tc.want {
				t.Fatalf("SupportsStreaming() = %v, want %v", got, tc.want)
			}
		})
	}
}
