package validate

import "errors"

var (
	ErrMissingName  = errors.New("missing name")
	ErrInvalidLimit = errors.New("invalid limit")
)

type Request struct {
	Name  string
	Limit int
}

func Validate(req Request) error {
	if req.Name == "" {
		return ErrMissingName
	}
	if req.Limit <= 0 {
		return ErrInvalidLimit
	}
	return nil
}
