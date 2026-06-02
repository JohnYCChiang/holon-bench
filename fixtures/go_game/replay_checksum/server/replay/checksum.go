package replay

type Event struct {
	Tick   int
	Player string
	Action string
}

func Checksum(events []Event) string {
	return "count"
}
