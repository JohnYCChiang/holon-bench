package framing

import (
	"io"
	"testing"
)

// oneByteReader returns at most one byte per Read call, then io.EOF.
type oneByteReader struct {
	data []byte
	pos  int
}

func (r *oneByteReader) Read(p []byte) (int, error) {
	if r.pos >= len(r.data) {
		return 0, io.EOF
	}
	if len(p) == 0 {
		return 0, nil
	}
	p[0] = r.data[r.pos]
	r.pos++
	return 1, nil
}

func TestReadFrameAcrossPartialReads(t *testing.T) {
	r := &oneByteReader{data: []byte("hello world")}
	got, err := ReadFrame(r, 5)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if string(got) != "hello" {
		t.Fatalf("ReadFrame = %q, want %q", got, "hello")
	}
}
