package combat

import "testing"

func TestDeathResetsStreak(t *testing.T) {
	tr := NewTracker()
	tr.Kill("a")
	tr.Kill("a")
	tr.Death("a")
	if tr.Current("a") != 0 {
		t.Fatalf("current=%d want 0 after death", tr.Current("a"))
	}
	if tr.Best("a") != 2 {
		t.Fatalf("best=%d want 2", tr.Best("a"))
	}
}

func TestBestTracksPeak(t *testing.T) {
	tr := NewTracker()
	tr.Kill("a")
	tr.Kill("a")
	tr.Kill("a")
	if tr.Best("a") != 3 {
		t.Fatalf("best=%d want 3", tr.Best("a"))
	}
}
