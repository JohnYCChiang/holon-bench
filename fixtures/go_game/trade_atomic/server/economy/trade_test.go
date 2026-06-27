package economy

import "testing"

func TestTradeSwapsWhenBothOwn(t *testing.T) {
	a := NewInventory("sword")
	b := NewInventory("shield")
	if !Trade(a, "sword", b, "shield") {
		t.Fatal("valid trade should succeed")
	}
	if a.Has("sword") || !a.Has("shield") {
		t.Fatal("a should now hold shield")
	}
	if b.Has("shield") || !b.Has("sword") {
		t.Fatal("b should now hold sword")
	}
}

func TestTradeRejectedWhenSellerLacksItem(t *testing.T) {
	a := NewInventory("sword")
	b := NewInventory()
	if Trade(a, "sword", b, "shield") {
		t.Fatal("b lacks shield -> reject")
	}
	if !a.Has("sword") {
		t.Fatal("a must keep sword on failed trade")
	}
	if b.Has("sword") {
		t.Fatal("no item should have moved to b")
	}
}
