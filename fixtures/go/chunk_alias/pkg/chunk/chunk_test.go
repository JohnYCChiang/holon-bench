package chunk

import (
	"reflect"
	"testing"
)

func TestChunkBasic(t *testing.T) {
	got := Chunk([]int{1, 2, 3, 4, 5}, 2)
	want := [][]int{{1, 2}, {3, 4}, {5}}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("Chunk() = %v, want %v", got, want)
	}
}

func TestChunkAppendDoesNotCorrupt(t *testing.T) {
	s := []int{1, 2, 3, 4}
	chunks := Chunk(s, 2)
	_ = append(chunks[0], 99)
	if !reflect.DeepEqual(s, []int{1, 2, 3, 4}) {
		t.Fatalf("append corrupted source: %v", s)
	}
	if !reflect.DeepEqual(chunks[1], []int{3, 4}) {
		t.Fatalf("append corrupted next chunk: %v", chunks[1])
	}
}
