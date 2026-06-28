package ready

import "testing"

func TestNotAllReady(t *testing.T) {
	c := NewCheck()
	c.Join("a")
	c.Join("b")
	c.SetReady("a")
	if c.AllReady() {
		t.Fatal("match must not start while b is not ready")
	}
	c.SetReady("b")
	if !c.AllReady() {
		t.Fatal("match must start once all are ready")
	}
}

func TestEmptyNotReady(t *testing.T) {
	c := NewCheck()
	if c.AllReady() {
		t.Fatal("empty check must not be ready")
	}
}
