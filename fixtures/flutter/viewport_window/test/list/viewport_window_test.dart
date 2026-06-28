import 'package:flutter_test/flutter_test.dart';
import 'package:viewport_window/list/viewport_window.dart';

void main() {
  test('computes the visible range at the top of a long list', () {
    expect(
      visibleRange(
        scrollOffset: 0,
        viewportExtent: 200,
        itemExtent: 50,
        itemCount: 100,
      ),
      (firstIndex: 0, lastIndex: 3),
    );
    expect(
      visibleRange(
        scrollOffset: 100,
        viewportExtent: 200,
        itemExtent: 50,
        itemCount: 100,
      ),
      (firstIndex: 2, lastIndex: 5),
    );
  });
}
