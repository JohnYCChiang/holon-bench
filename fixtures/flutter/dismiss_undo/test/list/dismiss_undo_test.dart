import 'package:flutter_test/flutter_test.dart';
import 'package:dismiss_undo/list/dismiss_undo.dart';

void main() {
  test('undo restores a dismissed item at its original index', () {
    final list = DismissList<String>(['a', 'b', 'c']);
    list.dismiss(1);
    expect(list.items, ['a', 'c']);
    expect(list.undo(), isTrue);
    expect(list.items, ['a', 'b', 'c']);
  });
}
