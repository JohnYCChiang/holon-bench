package rank

import "testing"

func TestUpdateSortedAndCapped(t *testing.T) {
	b := NewBoard(3)
	b.Update("a", 10)
	b.Update("b", 30)
	b.Update("c", 20)
	out := b.Update("d", 25)
	if len(out) != 3 {
		t.Fatalf("cap not enforced: %v", out)
	}
	want := []string{"b", "d", "c"}
	for i, e := range out {
		if e.ID != want[i] {
			t.Fatalf("rank[%d]=%s want %s (%v)", i, e.ID, want[i], out)
		}
	}
}

func TestUpdateReplacesSamePlayer(t *testing.T) {
	b := NewBoard(5)
	b.Update("a", 10)
	out := b.Update("a", 99)
	if len(out) != 1 {
		t.Fatalf("player duplicated: %v", out)
	}
	if out[0].Score != 99 {
		t.Fatalf("score not replaced: %v", out)
	}
}
