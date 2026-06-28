package framing

import "io"

// ReadFrame reads exactly size bytes from r and returns them in a new slice.
// An io.Reader may return fewer bytes than requested per Read call, so
// ReadFrame must keep reading until size bytes have been read. It returns
// io.ErrUnexpectedEOF if the stream ends after a partial frame and io.EOF if
// the stream ends before any byte of the frame is read.
func ReadFrame(r io.Reader, size int) ([]byte, error) {
	buf := make([]byte, size)
	n, err := r.Read(buf)
	if err != nil {
		return nil, err
	}
	return buf[:n], nil
}
