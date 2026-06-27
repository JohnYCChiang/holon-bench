package report

import (
	"reflect"
	"testing"
)

func TestSummarizeCountDescNameAsc(t *testing.T) {
	events := []Event{{Name: "a", Count: 1}, {Name: "c", Count: 3}, {Name: "b", Count: 3}}
	got := Summarize(events)
	want := []string{"b=3", "c=3", "a=1"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("Summarize() = %v, want %v", got, want)
	}
}
