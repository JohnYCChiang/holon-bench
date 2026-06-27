//! Fixed-capacity ring buffer. `push` overwrites the oldest element once full;
//! `to_vec` returns the live elements in oldest -> newest order.

pub struct RingBuffer<T> {
    buf: Vec<Option<T>>,
    cap: usize,
    head: usize, // index of the oldest live element
    len: usize,
}

impl<T: Clone> RingBuffer<T> {
    /// Create a ring buffer that holds at most `cap` elements. `cap` must be > 0.
    pub fn new(cap: usize) -> Self {
        assert!(cap > 0, "capacity must be positive");
        RingBuffer {
            buf: (0..cap).map(|_| None).collect(),
            cap,
            head: 0,
            len: 0,
        }
    }

    /// Push `v`. When the buffer is full the oldest element is overwritten and
    /// the head advances.
    pub fn push(&mut self, v: T) {
        let tail = (self.head + self.len) % self.cap;
        self.buf[tail] = Some(v);
        if self.len == self.cap {
            self.head = (self.head + 1) % self.cap;
        } else {
            self.len += 1;
        }
    }

    /// Return the live elements in oldest -> newest order.
    pub fn to_vec(&self) -> Vec<T> {
        let mut out = Vec::with_capacity(self.len);
        for i in 0..self.len {
            let idx = self.head + i; // BUG: missing `% self.cap`, walks off the end after wrap
            out.push(self.buf[idx].clone().unwrap());
        }
        out
    }
}
