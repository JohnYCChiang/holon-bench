package parse

import (
	"errors"
	"strconv"
	"strings"
	"time"
)

var ErrInvalidDuration = errors.New("invalid duration")

func Duration(input string) (time.Duration, error) {
	if strings.HasSuffix(input, "ms") {
		value, err := strconv.Atoi(strings.TrimSuffix(input, "ms"))
		if err != nil {
			return 0, err
		}
		return time.Duration(value) * time.Millisecond, nil
	}
	value, err := strconv.Atoi(strings.TrimSuffix(input, "s"))
	if err != nil {
		return 0, err
	}
	return time.Duration(value) * time.Second, nil
}
