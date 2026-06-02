import 'package:flutter_test/flutter_test.dart';
import 'package:timer_lifecycle/state/ticker_controller.dart';

void main() {
  test('dispose stops callbacks and is idempotent', () async {
    var ticks = 0;
    final controller = TickerController(() => ticks++);
    controller.start();
    await Future<void>.delayed(const Duration(milliseconds: 35));
    controller.dispose();
    controller.dispose();
    final afterDispose = ticks;
    await Future<void>.delayed(const Duration(milliseconds: 35));

    expect(ticks, afterDispose);
  });
}
