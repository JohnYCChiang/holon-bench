package economy

import "testing"

func TestDebitAffordable(t *testing.T) {
	if got := Apply(100, Transaction{Amount: -30, ClientBalance: 999}); got != 70 {
		t.Fatalf("debit wrong: got %d want 70", got)
	}
}

func TestDebitRejectedWhenUnaffordable(t *testing.T) {
	if got := Apply(20, Transaction{Amount: -50, ClientBalance: 999}); got != 20 {
		t.Fatalf("unaffordable debit applied: got %d want 20", got)
	}
}

func TestCreditCappedAtMax(t *testing.T) {
	if got := Apply(MaxGold-5, Transaction{Amount: 100}); got != MaxGold {
		t.Fatalf("credit not capped: got %d want %d", got, MaxGold)
	}
}
