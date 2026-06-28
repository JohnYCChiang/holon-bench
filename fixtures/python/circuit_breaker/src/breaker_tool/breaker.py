class CircuitBreaker:
    def __init__(self, threshold, reset_timeout, clock):
        self.threshold = threshold
        self.reset_timeout = reset_timeout
        self.clock = clock
        self.failures = 0
        self._state = "closed"
        self.opened_at = None

    def allow(self):
        if self._state == "open":
            if self.clock() - self.opened_at > self.reset_timeout:
                self._state = "half_open"
                return True
            return False
        return True

    def record_success(self):
        self._state = "closed"
        self.opened_at = None

    def record_failure(self):
        self.failures += 1
        if self.failures >= self.threshold:
            self._open()

    def _open(self):
        self._state = "open"
        self.opened_at = self.clock()

    def state(self):
        return self._state
