package replay

import "testing"

func TestFlattenReplayIsDeterministicByPlayerID(t *testing.T) {
	input := map[string][]Event{
		"b": {{Tick: 1, Kind: "move"}, {Tick: 2, Kind: "fire"}},
		"a": {{Tick: 1, Kind: "join"}},
	}
	got := Flatten(input)
	want := []string{"a:join", "b:move", "b:fire"}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("flatten = %#v, want %#v", got, want)
		}
	}
}
