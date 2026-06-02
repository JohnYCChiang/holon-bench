package store

type Store interface {
	Put(key string, value string) error
}

type MemoryStore struct {
	Values map[string]string
}

func (m *MemoryStore) Put(key string, value string) error {
	if m.Values == nil {
		m.Values = map[string]string{}
	}
	m.Values[key] = value
	return nil
}

func Save(store Store, key string, value string) error {
	return store.Put(key, value)
}
