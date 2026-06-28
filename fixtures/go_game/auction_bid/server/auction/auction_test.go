package auction

import "testing"

func TestOutbidRefundsPrevious(t *testing.T) {
	h := NewHouse(1)
	h.Deposit("a", 100)
	h.Deposit("b", 100)
	if !h.Bid("a", 10) {
		t.Fatal("first valid bid should be accepted")
	}
	if !h.Bid("b", 20) {
		t.Fatal("higher bid should be accepted")
	}
	if h.Balance("a") != 100 {
		t.Fatalf("outbid player a not refunded: balance=%d want 100", h.Balance("a"))
	}
	if h.Balance("b") != 80 {
		t.Fatalf("bidder b balance=%d want 80", h.Balance("b"))
	}
}

func TestMinIncrementEnforced(t *testing.T) {
	h := NewHouse(5)
	h.Deposit("a", 100)
	h.Deposit("b", 100)
	h.Bid("a", 10)
	if h.Bid("b", 12) {
		t.Fatal("bid below min increment must be rejected")
	}
}
