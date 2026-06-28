import 'package:flutter_test/flutter_test.dart';
import 'package:connectivity_retry/net/retry_runner.dart';

void main() {
  test('retries until the action succeeds', () async {
    final delays = <Duration>[];
    final runner = RetryRunner(
      maxAttempts: 5,
      baseDelay: const Duration(milliseconds: 100),
      sleep: (d) async => delays.add(d),
    );

    var attempts = 0;
    final result = await runner.run((attempt) async {
      attempts++;
      if (attempts < 3) throw StateError('offline');
      return 'ok';
    });

    expect(result, 'ok');
    expect(attempts, 3);
  });
}
