package matchmaking

import "testing"

func TestPicksClosestMMR(t *testing.T) {
	pool := []Ticket{
		{PlayerID: 1, MMR: 1600, EnqueueTick: 0},
		{PlayerID: 2, MMR: 1520, EnqueueTick: 0},
		{PlayerID: 3, MMR: 1490, EnqueueTick: 0},
	}
	if got := FindOpponent(pool, Ticket{PlayerID: 9, MMR: 1500}, 200); got != 3 {
		t.Fatalf("closest opponent wrong: got %d want 3", got)
	}
}

func TestRejectsOutOfSpread(t *testing.T) {
	pool := []Ticket{{PlayerID: 1, MMR: 2000, EnqueueTick: 0}}
	if got := FindOpponent(pool, Ticket{PlayerID: 9, MMR: 1000}, 100); got != -1 {
		t.Fatalf("out-of-spread matched: got %d want -1", got)
	}
}

func TestExcludesSelf(t *testing.T) {
	pool := []Ticket{{PlayerID: 9, MMR: 1500, EnqueueTick: 0}}
	if got := FindOpponent(pool, Ticket{PlayerID: 9, MMR: 1500}, 100); got != -1 {
		t.Fatalf("matched self: got %d want -1", got)
	}
}
