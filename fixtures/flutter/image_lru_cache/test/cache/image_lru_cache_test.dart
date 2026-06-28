import 'package:flutter_test/flutter_test.dart';
import 'package:image_lru_cache/cache/image_lru_cache.dart';

void main() {
  test('evicts the least-recently-used entry when over capacity', () {
    final cache = ImageLruCache(30);
    cache.put('a', 10);
    cache.put('b', 10);
    cache.put('c', 10); // used = 30, at capacity
    cache.get('a'); // 'a' becomes most-recently-used
    cache.put('d', 10); // must evict 'b' (now LRU)

    expect(cache.get('b'), isNull);
    expect(cache.get('a'), 10);
    expect(cache.get('d'), 10);
    expect(cache.usedBytes, 30);
  });
}
