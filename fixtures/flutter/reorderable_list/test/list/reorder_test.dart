import 'package:flutter_test/flutter_test.dart';
import 'package:reorderable_list/list/reorder.dart';

void main() {
  test('moving an item downward uses ReorderableListView index semantics', () {
    // Move 'a' (index 0) to after 'b'; the callback reports newIndex = 2.
    expect(reorder(['a', 'b', 'c'], 0, 2), ['b', 'a', 'c']);
  });
}
