package sim

import "testing"

func TestRejectsOutOfOrderInput(t *testing.T) {
	state := NewState()
	if result := state.Apply(Input{PlayerID: "p1", Seq: 1, DeltaX: 5}); !result.Accepted {
		t.Fatalf("first input should be accepted: %#v", result)
	}
	result := state.Apply(Input{PlayerID: "p1", Seq: 1, DeltaX: 99})
	if !result.Ignored || result.Accepted || result.Invalid != 1 {
		t.Fatalf("duplicate input should be ignored with invalid count, got %#v", result)
	}
	if state.X["p1"] != 5 {
		t.Fatalf("duplicate input corrupted state: x=%d", state.X["p1"])
	}
}

func TestTracksSequencePerPlayer(t *testing.T) {
	state := NewState()
	state.Apply(Input{PlayerID: "p1", Seq: 10, DeltaX: 1})
	result := state.Apply(Input{PlayerID: "p2", Seq: 1, DeltaX: 2})
	if !result.Accepted {
		t.Fatalf("p2 sequence should be independent: %#v", result)
	}
	if state.X["p2"] != 2 {
		t.Fatalf("p2 state not updated")
	}
}
