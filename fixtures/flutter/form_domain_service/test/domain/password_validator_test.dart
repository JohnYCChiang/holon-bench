import 'package:flutter_test/flutter_test.dart';
import 'package:form_domain_service/domain/password_validator.dart';

void main() {
  test('password validator reports required and length errors', () {
    expect(validatePassword(''), 'Enter a password');
    expect(validatePassword('short'), 'Use at least 8 characters');
    expect(validatePassword('long-enough'), isNull);
  });
}
