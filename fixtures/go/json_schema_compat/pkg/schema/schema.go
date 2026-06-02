package schema

import "encoding/json"

type Request struct {
	Name      string `json:"name"`
	TimeoutMS int    `json:"timeout_ms"`
	DryRun    bool   `json:"dry_run"`
}

func DecodeRequest(data []byte) (Request, error) {
	var req Request
	err := json.Unmarshal(data, &req)
	return req, err
}

func EncodeRequest(req Request) ([]byte, error) {
	return json.Marshal(req)
}
