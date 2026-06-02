package tool

import "context"

type Request struct {
	Input string
}

type Result struct {
	Output string
}

type Runner interface {
	Run(context.Context, Request) (Result, error)
}
