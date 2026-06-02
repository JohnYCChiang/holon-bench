package schema

import (
	"bytes"
	"encoding/json"
	"testing"
)

func TestDecodeRequestCompatibility(t *testing.T) {
	tests := []struct {
		name string
		raw  string
		want Request
	}{
		{name: "all fields", raw: `{"name":"job","timeout_ms":250,"dry_run":true}`, want: Request{Name: "job", TimeoutMS: 250, DryRun: true}},
		{name: "missing optional fields", raw: `{"name":"job"}`, want: Request{Name: "job"}},
		{name: "zero timeout preserved", raw: `{"name":"job","timeout_ms":0}`, want: Request{Name: "job"}},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			got, err := DecodeRequest([]byte(tc.raw))
			if err != nil {
				t.Fatalf("DecodeRequest returned error: %v", err)
			}
			if got != tc.want {
				t.Fatalf("DecodeRequest() = %#v, want %#v", got, tc.want)
			}
		})
	}
}

func TestDecodeRequestRejectsUnknownFields(t *testing.T) {
	_, err := DecodeRequest([]byte(`{"name":"job","extra":true}`))
	if err == nil {
		t.Fatal("expected unknown field error")
	}
}

func TestEncodeRequestOmitsFalseDryRun(t *testing.T) {
	data, err := EncodeRequest(Request{Name: "job", TimeoutMS: 0})
	if err != nil {
		t.Fatalf("EncodeRequest returned error: %v", err)
	}
	if bytes.Contains(data, []byte("dry_run")) {
		t.Fatalf("dry_run=false should be omitted, got %s", data)
	}
	var decoded map[string]any
	if err := json.Unmarshal(data, &decoded); err != nil {
		t.Fatalf("encoded JSON invalid: %v", err)
	}
	if _, ok := decoded["timeout_ms"]; !ok {
		t.Fatalf("timeout_ms field should remain present, got %s", data)
	}
}
