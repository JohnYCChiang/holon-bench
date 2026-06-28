import 'package:flutter_test/flutter_test.dart';
import 'package:currency_input_format/format/currency_formatter.dart';

void main() {
  test('formats cents with grouping and two decimals', () {
    expect(formatCents(0), '\$0.00');
    expect(formatCents(5), '\$0.05');
    expect(formatCents(1234567), '\$12,345.67');
  });
}
