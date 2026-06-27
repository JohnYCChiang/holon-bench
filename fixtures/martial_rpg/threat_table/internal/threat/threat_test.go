package threat

import "testing"

func TestHighestThreatChosen(t *testing.T) {
	tbl := Table{Units: []Unit{{1, 10}, {2, 30}, {3, 20}}}
	if got := Target(tbl, Input{}); got != 2 {
		t.Fatalf("target = %d, want 2", got)
	}
}

func TestTieBrokenByLowerID(t *testing.T) {
	tbl := Table{Units: []Unit{{5, 40}, {2, 40}}}
	if got := Target(tbl, Input{}); got != 2 {
		t.Fatalf("target = %d, want 2", got)
	}
}

func TestEmptyTableReturnsMinusOne(t *testing.T) {
	if got := Target(Table{}, Input{}); got != -1 {
		t.Fatalf("target = %d, want -1", got)
	}
}
