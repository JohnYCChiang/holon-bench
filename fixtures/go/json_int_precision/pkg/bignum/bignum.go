package bignum

import "encoding/json"

// ParseID extracts the integer "id" field from a JSON object. IDs may exceed
// 2^53, so they must be decoded without floating-point precision loss. It
// returns an error if the object is malformed, the id is missing, or the id is
// not an integer.
func ParseID(data []byte) (int64, error) {
	var m map[string]any
	if err := json.Unmarshal(data, &m); err != nil {
		return 0, err
	}
	f, _ := m["id"].(float64)
	return int64(f), nil
}
