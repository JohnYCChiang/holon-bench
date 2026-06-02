package store

import "testing"

type flushingStore struct {
	MemoryStore
	flushed bool
}

func (s *flushingStore) Flush() error {
	s.flushed = true
	return nil
}

func TestSaveUsesOptionalFlush(t *testing.T) {
	s := &flushingStore{}
	if err := Save(s, "a", "b"); err != nil {
		t.Fatalf("Save returned error: %v", err)
	}
	if !s.flushed {
		t.Fatal("expected optional Flush to be called")
	}
}

func TestSaveDoesNotRequireFlush(t *testing.T) {
	s := &MemoryStore{}
	if err := Save(s, "a", "b"); err != nil {
		t.Fatalf("Save returned error: %v", err)
	}
}
