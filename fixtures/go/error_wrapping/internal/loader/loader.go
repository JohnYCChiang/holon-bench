package loader

import (
	"encoding/json"
	"errors"
	"fmt"
)

var ErrInvalidConfig = errors.New("invalid config")

type Config struct {
	Name string `json:"name"`
}

type Reader func(path string) ([]byte, error)

func LoadConfig(path string, read Reader) (*Config, error) {
	if path == "" {
		return nil, ErrInvalidConfig
	}
	data, err := read(path)
	if err != nil {
		return nil, fmt.Errorf("load config %q failed", path)
	}
	var cfg Config
	if err := json.Unmarshal(data, &cfg); err != nil {
		return nil, ErrInvalidConfig
	}
	if cfg.Name == "" {
		return nil, ErrInvalidConfig
	}
	return &cfg, nil
}
