package runtime

import "sync"

type Server struct {
	mu      sync.Mutex
	closed  bool
	events  chan string
	handled []string
}

func NewServer() *Server {
	return &Server{events: make(chan string), handled: []string{}}
}

func (s *Server) Start() {
	go func() {
		for event := range s.events {
			s.handled = append(s.handled, event)
		}
	}()
}

func (s *Server) Submit(event string) bool {
	if s.closed {
		return false
	}
	s.events <- event
	return true
}

func (s *Server) Shutdown() {
	s.closed = true
	close(s.events)
}

func (s *Server) Handled() []string {
	return append([]string(nil), s.handled...)
}
