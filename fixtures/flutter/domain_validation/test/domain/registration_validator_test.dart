import 'package:domain_validation/domain/registration_validator.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('validates email in domain service', () {
    expect(validateRegistrationEmail('bad'), 'Enter a valid email');
    expect(validateRegistrationEmail('user@example.com'), isNull);
  });
}
