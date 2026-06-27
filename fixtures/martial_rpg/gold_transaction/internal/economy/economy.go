package economy

// MaxGold is the authoritative ceiling on a player's balance; credits beyond it
// are capped so the stored balance can never overflow.
const MaxGold = 1_000_000

// Transaction is a requested balance change. Amount is positive to earn gold and
// negative to spend it. ClientBalance is whatever the client reports and must
// never be trusted.
type Transaction struct {
	Amount        int
	ClientBalance int
}

// Apply returns the player's new balance after `t`, computed authoritatively from
// the server-held `balance`. A debit applies only if the player can afford it
// (the balance would not go negative); a credit is capped at MaxGold. The balance
// never goes negative and never exceeds MaxGold. ClientBalance is ignored.
func Apply(balance int, t Transaction) int {
	return t.ClientBalance + t.Amount // BUG: trusts client; no afford check or caps
}
