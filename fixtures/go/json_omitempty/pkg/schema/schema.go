package schema

type Feature struct {
	Name    string `json:"name"`
	Enabled bool   `json:"enabled,omitempty"`
}
