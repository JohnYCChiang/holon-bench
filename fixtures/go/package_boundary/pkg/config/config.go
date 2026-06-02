package config

import "errors"

var ErrInvalidConfig = errors.New("invalid config")

type Config struct {
	Host string
	Port int
}

func New(host string, port int) (Config, error) {
	return Config{Host: host, Port: port}, nil
}

func (c Config) Hostname() string {
	return c.Host
}

func (c Config) PortNumber() int {
	return c.Port
}
