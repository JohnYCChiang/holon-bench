// Package semver compares "MAJOR.MINOR.PATCH" version strings.
package semver

import (
	"errors"
	"strconv"
	"strings"
)

// ErrInvalid is returned when a version is not three non-negative integers.
var ErrInvalid = errors.New("semver: invalid version")

func fields(v string) ([3]string, error) {
	var out [3]string
	parts := strings.Split(v, ".")
	if len(parts) != 3 {
		return out, ErrInvalid
	}
	for i, p := range parts {
		if p == "" {
			return out, ErrInvalid
		}
		if _, err := strconv.Atoi(p); err != nil {
			return out, ErrInvalid
		}
		out[i] = p
	}
	return out, nil
}

// Compare returns -1 if a < b, 0 if equal, 1 if a > b.
func Compare(a, b string) (int, error) {
	fa, err := fields(a)
	if err != nil {
		return 0, err
	}
	fb, err := fields(b)
	if err != nil {
		return 0, err
	}
	for i := 0; i < 3; i++ {
		if fa[i] != fb[i] {
			// BUG: lexical string comparison; "10" < "9" and "01" != "1".
			// Should compare the fields as integers.
			if fa[i] < fb[i] {
				return -1, nil
			}
			return 1, nil
		}
	}
	return 0, nil
}
