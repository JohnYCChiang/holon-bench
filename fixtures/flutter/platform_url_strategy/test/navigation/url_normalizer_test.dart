import 'package:flutter_test/flutter_test.dart';
import 'package:platform_url_strategy/navigation/url_normalizer.dart';

void main() {
  test('normalizes hash and path URLs to same logical route', () {
    expect(normalizeUrl('/#/items/42?tab=notes'), '/items/42?tab=notes');
    expect(normalizeUrl('/items/42?tab=notes'), '/items/42?tab=notes');
  });
}
