import 'package:flutter_test/flutter_test.dart';
import 'package:tab_retention/state/tab_state_store.dart';

void main() {
  test('each tab keeps its own saved offset across switches', () {
    final store = TabStateStore(3);
    store.switchTo(1);
    store.saveOffset(100);
    store.switchTo(0);
    store.saveOffset(50);
    store.switchTo(1);
    expect(store.activeOffset, 100);
  });
}
