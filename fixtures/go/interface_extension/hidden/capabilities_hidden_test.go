package tool

import (
	"context"
	"testing"
)

type pointerStreamingRunner struct{}

func (pointerStreamingRunner) Run(context.Context, Request) (Result, error) {
	return Result{Output: "pointer"}, nil
}

func (*pointerStreamingRunner) SupportsStreaming() bool {
	return true
}

type misleadingRunner struct{}

func (misleadingRunner) Run(context.Context, Request) (Result, error) {
	return Result{Output: "misleading"}, nil
}

func (misleadingRunner) StreamingSupported() bool {
	return true
}

func TestHiddenSupportsStreamingUsesExactOptionalInterface(t *testing.T) {
	if SupportsStreaming(pointerStreamingRunner{}) {
		t.Fatalf("value with pointer-only SupportsStreaming method must not satisfy optional interface")
	}
	if !SupportsStreaming(&pointerStreamingRunner{}) {
		t.Fatalf("pointer receiver implementation should satisfy optional interface")
	}
	if SupportsStreaming(misleadingRunner{}) {
		t.Fatalf("similar method names must not be treated as streaming support")
	}
}
