import 'package:flutter_test/flutter_test.dart';
import 'package:service_cache_ttl/services/profile_cache.dart';

void main() {
  test('cache reuses values inside ttl and refetches after expiry', () async {
    var now = DateTime(2026, 1, 1);
    var calls = 0;
    final cache = ProfileCache(
      ttl: const Duration(minutes: 5),
      now: () => now,
      fetch: () async => 'profile-${++calls}',
    );

    expect(await cache.get(), 'profile-1');
    now = now.add(const Duration(minutes: 2));
    expect(await cache.get(), 'profile-1');
    now = now.add(const Duration(minutes: 5));
    expect(await cache.get(), 'profile-2');
  });
}
