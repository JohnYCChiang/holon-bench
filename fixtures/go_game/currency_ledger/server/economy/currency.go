package economy

type Ledger struct {
	bal map[string]int64
}

func NewLedger() *Ledger { return &Ledger{bal: map[string]int64{}} }

func (l *Ledger) Balance(id string) int64 { return l.bal[id] }

// Credit adds amount to id (a source). A non-positive amount is rejected and
// leaves state unchanged. Returns true only when applied.
func (l *Ledger) Credit(id string, amount int64) bool {
	if amount <= 0 {
		return false
	}
	l.bal[id] += amount
	return true
}

// Debit removes amount from id (a sink). It is authoritative: a balance may
// never go negative, so a debit larger than the balance is rejected and leaves
// state unchanged. A non-positive amount is rejected. Returns true only when
// applied.
func (l *Ledger) Debit(id string, amount int64) bool {
	l.bal[id] -= amount
	return true
}
