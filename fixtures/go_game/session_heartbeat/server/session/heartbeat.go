package session

type Session struct {
	ID       string
	Deadline int
}

type Store struct {
	Sessions map[string]Session
	TTL      int
}

func (s *Store) Heartbeat(id string, now int) bool {
	session, ok := s.Sessions[id]
	if !ok {
		return false
	}
	session.Deadline = now
	s.Sessions[id] = session
	return true
}

func (s *Store) Expire(now int) []string {
	expired := []string{}
	for id, session := range s.Sessions {
		if session.Deadline <= now {
			expired = append(expired, id)
			delete(s.Sessions, id)
		}
	}
	return expired
}
