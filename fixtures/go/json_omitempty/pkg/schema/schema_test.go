package schema

import (
	"encoding/json"
	"testing"
)

func TestExplicitFalseRoundTrips(t *testing.T) {
	var feature Feature
	if err := json.Unmarshal([]byte(`{"name":"beta","enabled":false}`), &feature); err != nil {
		t.Fatal(err)
	}
	if feature.Enabled == nil {
		t.Fatal("explicit false should be distinguishable from missing enabled")
	}
	if *feature.Enabled {
		t.Fatal("expected explicit false")
	}
	encoded, err := json.Marshal(feature)
	if err != nil {
		t.Fatal(err)
	}
	if string(encoded) != `{"name":"beta","enabled":false}` {
		t.Fatalf("unexpected JSON: %s", encoded)
	}
}

func TestMissingEnabledOmitsField(t *testing.T) {
	encoded, err := json.Marshal(Feature{Name: "stable"})
	if err != nil {
		t.Fatal(err)
	}
	if string(encoded) != `{"name":"stable"}` {
		t.Fatalf("unexpected JSON: %s", encoded)
	}
}
