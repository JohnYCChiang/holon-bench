import 'package:flutter_test/flutter_test.dart';
import 'package:route_parser_refresh/navigation/route_parser.dart';

void main() {
  test('parses item route after refresh with query parameters', () {
    final route = parseRoute('/item/42?tab=notes');
    expect(route, isA<ItemRoute>());
    expect((route as ItemRoute).id, '42');
  });

  test('rejects incomplete item route', () {
    expect(parseRoute('/item/'), isA<HomeRoute>());
  });
}
