package economy

import "testing"

func TestDebitRejectedWhenInsufficient(t *testing.T) {
	l := NewLedger()
	l.Credit("a", 10)
	if l.Debit("a", 20) {
		t.Fatal("debit beyond balance must be rejected")
	}
	if l.Balance("a") != 10 {
		t.Fatalf("rejected debit mutated balance: %d", l.Balance("a"))
	}
}

func TestNonPositiveRejected(t *testing.T) {
	l := NewLedger()
	if l.Credit("a", 0) || l.Debit("a", -5) {
		t.Fatal("non-positive amounts must be rejected")
	}
	if l.Balance("a") != 0 {
		t.Fatalf("balance mutated: %d", l.Balance("a"))
	}
}
