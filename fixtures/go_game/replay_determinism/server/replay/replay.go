package replay

type Event struct {
	Tick int
	Kind string
}

func Flatten(events map[string][]Event) []string {
	out := []string{}
	for player, playerEvents := range events {
		for _, event := range playerEvents {
			out = append(out, player+":"+event.Kind)
		}
	}
	return out
}
