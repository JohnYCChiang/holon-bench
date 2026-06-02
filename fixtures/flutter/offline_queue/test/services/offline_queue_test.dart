import 'package:flutter_test/flutter_test.dart';
import 'package:offline_queue/services/offline_queue.dart';

void main() {
  test('keeps failed sends queued and preserves order', () async {
    final attempts = <String>[];
    final queue = OfflineQueue((message) async {
      attempts.add(message);
      return message != 'b';
    });
    queue.add('a');
    queue.add('b');
    queue.add('c');

    await queue.flush();

    expect(attempts, ['a', 'b', 'c']);
    expect(queue.pending, ['b']);
  });
}
