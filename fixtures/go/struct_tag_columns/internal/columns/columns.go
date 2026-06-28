package columns

import "reflect"

// Columns returns the database column names for the exported fields of the
// struct value v (a struct or pointer to struct). The column name comes from
// the `db` struct tag. A field tagged `db:"-"` is skipped. A field with no db
// tag falls back to its Go field name. Unexported fields are ignored.
func Columns(v any) []string {
	t := reflect.TypeOf(v)
	cols := []string{}
	for i := 0; i < t.NumField(); i++ {
		f := t.Field(i)
		cols = append(cols, f.Name)
	}
	return cols
}
