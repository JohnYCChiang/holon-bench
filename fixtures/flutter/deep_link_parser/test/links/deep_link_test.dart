import 'package:flutter_test/flutter_test.dart';
import 'package:deep_link_parser/links/deep_link.dart';

void main() {
  test('parses a product deep link with a ref query', () {
    final link = parseDeepLink('myapp://product/42?ref=home');
    expect(link, isA<ProductLink>());
    final product = link as ProductLink;
    expect(product.id, '42');
    expect(product.ref, 'home');
  });

  test('rejects links from a foreign scheme', () {
    expect(parseDeepLink('https://product/42'), isA<UnknownLink>());
  });
}
