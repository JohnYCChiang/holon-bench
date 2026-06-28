/// A byte-bounded LRU cache. The least-recently-used entry is evicted when a
/// new entry would push total bytes over [capacityBytes]. A `get` refreshes
/// recency; an entry larger than the capacity is rejected.
class ImageLruCache {
  ImageLruCache(this.capacityBytes);

  final int capacityBytes;
  final Map<String, int> _sizes = {};
  int _used = 0;

  int get usedBytes => _used;

  /// Keys ordered least-recently-used first.
  List<String> get keys => _sizes.keys.toList();

  int? get(String key) {
    return _sizes[key];
  }

  /// Returns false when [sizeBytes] alone exceeds the capacity.
  bool put(String key, int sizeBytes) {
    _sizes[key] = sizeBytes;
    _used += sizeBytes;
    return true;
  }
}
