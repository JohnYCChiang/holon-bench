import 'package:flutter_test/flutter_test.dart';
import 'package:derived_selector/state/derived_store.dart';

void main() {
  test('listeners fire only when the derived bucket changes', () {
    final store = DerivedStore(0);
    final seen = <int>[];
    store.listen(seen.add);

    store.set(5); // bucket 0 -> 0, no notification
    store.set(12); // bucket 0 -> 1, notify
    store.set(15); // bucket 1 -> 1, no notification
    store.set(23); // bucket 1 -> 2, notify

    expect(seen, [1, 2]);
  });
}
