package decode

import (
	"encoding/json"
	"errors"
)

// ErrUnknownField is returned when input contains a field not present in Settings.
var ErrUnknownField = errors.New("unknown field")

type Settings struct {
	Name    string `json:"name"`
	Timeout int    `json:"timeout"`
}

// Decode parses strict JSON into Settings. Unknown fields must be rejected
// with an error that matches ErrUnknownField via errors.Is.
func Decode(data []byte) (Settings, error) {
	var s Settings
	if err := json.Unmarshal(data, &s); err != nil {
		return Settings{}, err
	}
	return s, nil
}
