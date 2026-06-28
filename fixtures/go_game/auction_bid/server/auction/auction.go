package auction

// House is an authoritative single-lot auction with escrow. Bidders deposit
// funds; a bid moves funds into escrow and refunds the previously winning
// bidder. A bid must beat the current high bid by at least the minimum
// increment and the bidder must have sufficient balance. No currency is ever
// created or destroyed.
type House struct {
	bal        map[string]int64
	minInc     int64
	highBid    int64
	highBidder string
	escrow     int64
	open       bool
}

func NewHouse(minInc int64) *House {
	return &House{bal: map[string]int64{}, minInc: minInc, open: true}
}

// Deposit adds external funds to a bidder's balance.
func (h *House) Deposit(id string, amt int64) {
	if amt <= 0 || id == "" {
		return
	}
	h.bal[id] += amt
}

func (h *House) Balance(id string) int64 { return h.bal[id] }
func (h *House) HighBid() int64          { return h.highBid }
func (h *House) HighBidder() string      { return h.highBidder }
func (h *House) Escrow() int64           { return h.escrow }

// Bid places a bid of amt by id. It is accepted only if the auction is open,
// amt is at least the current high bid plus the minimum increment (or at least
// minInc for the first bid), and the bidder has enough balance. On success the
// funds move to escrow and the previous high bidder is refunded.
func (h *House) Bid(id string, amt int64) bool {
	if !h.open {
		return false
	}
	if amt <= h.highBid { // BUG: ignores minInc, balance, and refunding the previous leader.
		return false
	}
	h.bal[id] -= amt
	h.escrow += amt
	h.highBid = amt
	h.highBidder = id
	return true
}

// Close ends the auction and returns the winning bidder and price.
func (h *House) Close() (string, int64) {
	h.open = false
	return h.highBidder, h.highBid
}
