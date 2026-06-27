package ladder

import "testing"

func TestWinRaisesRating(t *testing.T) {
	// equal ratings, K=32, win: delta = round(32 * (1 - 0.5)) = 16
	got := Update(Match{PlayerRating: 1500, OpponentRating: 1500, K: 32, Outcome: 2})
	if got != 1516 {
		t.Fatalf("new rating = %d, want 1516", got)
	}
}

func TestLossLowersRating(t *testing.T) {
	// equal ratings, K=32, loss: delta = round(32 * (0 - 0.5)) = -16
	got := Update(Match{PlayerRating: 1500, OpponentRating: 1500, K: 32, Outcome: 0})
	if got != 1484 {
		t.Fatalf("new rating = %d, want 1484", got)
	}
}

func TestIgnoresClientRating(t *testing.T) {
	// equal ratings, draw: rating is unchanged regardless of the client's claim
	got := Update(Match{PlayerRating: 1500, OpponentRating: 1500, K: 32, Outcome: 1, ClientNewRating: 9999})
	if got != 1500 {
		t.Fatalf("client rating trusted: new rating = %d, want 1500", got)
	}
}
