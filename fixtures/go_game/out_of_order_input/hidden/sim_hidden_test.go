package sim

import "testing"

func TestHiddenRejectsOlderInputAfterLaterAcceptedInput(t *testing.T) {
	state := NewState()
	if result := state.Apply(Input{PlayerID: "p1", Seq: 2, DeltaX: 10}); !result.Accepted {
		t.Fatalf("new input should be accepted: %#v", result)
	}
	result := state.Apply(Input{PlayerID: "p1", Seq: 1, DeltaX: -99})
	if !result.Ignored || result.Accepted || result.Invalid != 1 {
		t.Fatalf("older input should be ignored with invalid marker: %#v", result)
	}
	if got := state.X["p1"]; got != 10 {
		t.Fatalf("older input corrupted state: got x=%d", got)
	}
	if got := state.LastSeq["p1"]; got != 2 {
		t.Fatalf("older input changed last sequence: got %d", got)
	}
}

func TestHiddenOutOfOrderIsPerPlayer(t *testing.T) {
	state := NewState()
	state.Apply(Input{PlayerID: "p1", Seq: 10, DeltaX: 1})
	state.Apply(Input{PlayerID: "p2", Seq: 3, DeltaX: 5})

	result := state.Apply(Input{PlayerID: "p2", Seq: 2, DeltaX: 100})
	if !result.Ignored || result.Accepted {
		t.Fatalf("p2 old input should be ignored independently: %#v", result)
	}
	if got := state.X["p1"]; got != 1 {
		t.Fatalf("p1 state changed unexpectedly: %d", got)
	}
	if got := state.X["p2"]; got != 5 {
		t.Fatalf("p2 old input corrupted state: %d", got)
	}
}
