import 'package:flutter_test/flutter_test.dart';
import 'package:search_history/state/search_history.dart';

void main() {
  test('repeated queries move to the front without duplicating', () {
    final h = SearchHistory();
    h.record('a');
    h.record('b');
    h.record('a');
    expect(h.entries, ['a', 'b']);
  });
}
