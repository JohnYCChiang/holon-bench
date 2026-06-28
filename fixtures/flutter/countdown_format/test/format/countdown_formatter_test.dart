import 'package:flutter_test/flutter_test.dart';
import 'package:countdown_format/format/countdown_formatter.dart';

void main() {
  test('formats minutes and seconds with zero padding', () {
    expect(formatCountdown(65), '01:05');
    expect(formatCountdown(600), '10:00');
  });
}
