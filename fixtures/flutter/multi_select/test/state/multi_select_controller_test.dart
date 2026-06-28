import 'package:flutter_test/flutter_test.dart';
import 'package:multi_select/state/multi_select_controller.dart';

void main() {
  test('toggling the same id twice clears it', () {
    final c = SelectionController();
    c.toggle('a');
    expect(c.isSelected('a'), isTrue);
    c.toggle('a');
    expect(c.isSelected('a'), isFalse);
    expect(c.count, 0);
  });
}
