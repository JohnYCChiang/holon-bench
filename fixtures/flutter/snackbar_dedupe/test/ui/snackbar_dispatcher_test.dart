import 'package:flutter_test/flutter_test.dart';
import 'package:snackbar_dedupe/ui/snackbar_dispatcher.dart';

void main() {
  test('a repeated identical message within the window is suppressed', () {
    var t = DateTime(2026, 1, 1);
    final d = SnackbarDispatcher(
      now: () => t,
      window: const Duration(seconds: 3),
    );

    expect(d.show('Saved'), isTrue);
    t = t.add(const Duration(seconds: 1));
    expect(d.show('Saved'), isFalse);
  });
}
