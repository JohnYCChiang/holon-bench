import 'package:flutter_test/flutter_test.dart';
import 'package:locale_number_format/format/number_formatter.dart';

void main() {
  test('groups thousands with the default separator', () {
    expect(formatThousands(1234), '1,234');
    expect(formatThousands(1234567), '1,234,567');
  });
}
