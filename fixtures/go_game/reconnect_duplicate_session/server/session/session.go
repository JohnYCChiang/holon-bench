package session

import "time"

type Session struct {
	ID        string
	PlayerID  string
	LobbyID   string
	ExpiresAt time.Time
}

type Store struct {
	next     int
	byToken  map[string]*Session
	lobbyIDs map[string][]string
	now      func() time.Time
}

func NewStore(now func() time.Time) *Store {
	return &Store{byToken: map[string]*Session{}, lobbyIDs: map[string][]string{}, now: now}
}

func (s *Store) Create(token, playerID, lobbyID string, ttl time.Duration) *Session {
	s.next++
	sess := &Session{ID: token, PlayerID: playerID, LobbyID: lobbyID, ExpiresAt: s.now().Add(ttl)}
	s.byToken[token] = sess
	s.lobbyIDs[lobbyID] = append(s.lobbyIDs[lobbyID], playerID)
	return sess
}

func (s *Store) Reconnect(token string) (*Session, bool) {
	old := s.byToken[token]
	if old == nil || !old.ExpiresAt.After(s.now()) {
		return nil, false
	}
	return s.Create(token, old.PlayerID, old.LobbyID, time.Minute), true
}

func (s *Store) LobbyMembers(lobbyID string) []string {
	return append([]string(nil), s.lobbyIDs[lobbyID]...)
}
