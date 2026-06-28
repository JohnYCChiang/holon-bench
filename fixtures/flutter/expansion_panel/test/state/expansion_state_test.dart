import 'package:flutter_test/flutter_test.dart';
import 'package:expansion_panel/state/expansion_state.dart';

void main() {
  test('multi-open mode keeps several panels open at once', () {
    final s = ExpansionState();
    s.toggle(0);
    s.toggle(1);
    expect(s.openPanels, {0, 1});
  });
}
