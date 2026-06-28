import 'package:flutter_test/flutter_test.dart';
import 'package:input_mask/format/input_mask.dart';

void main() {
  test('fills a full phone mask', () {
    expect(applyMask('1234567890', '(###) ###-####'), '(123) 456-7890');
  });
}
