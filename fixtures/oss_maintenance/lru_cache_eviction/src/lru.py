class LRUCache:
    """Fixed-capacity cache that evicts the least recently used entry.

    Both ``get`` and ``put`` count as a use: the affected key becomes
    most-recently used. ``get`` returns the stored value or None on a miss.
    ``put`` on an existing key updates its value and marks it most-recently
    used; inserting a new key past ``capacity`` evicts the least recently used
    entry. ``capacity`` must be positive.
    """

    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        # Insertion order is recency order: the first key is the oldest (LRU).
        self._data = {}

    def get(self, key):
        if key not in self._data:
            return None
        value = self._data[key]
        # BUG: a successful get must refresh recency (move key to most-recent).
        return value

    def put(self, key, value):
        if key in self._data:
            del self._data[key]
        elif len(self._data) >= self.capacity:
            oldest = next(iter(self._data))
            del self._data[oldest]
        self._data[key] = value
