package columns

import (
	"reflect"
	"testing"
)

type Row struct {
	ID    int    `db:"id"`
	Name  string `db:"name"`
	Temp  string `db:"-"`
	Extra string
}

func TestColumnsUsesTags(t *testing.T) {
	got := Columns(Row{})
	want := []string{"id", "name", "Extra"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("Columns() = %v, want %v", got, want)
	}
}
