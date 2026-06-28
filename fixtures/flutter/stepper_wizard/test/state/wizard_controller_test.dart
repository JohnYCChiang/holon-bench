import 'package:flutter_test/flutter_test.dart';
import 'package:stepper_wizard/state/wizard_controller.dart';

void main() {
  test('next advances only when the current step is valid', () {
    final w = WizardController(3);
    expect(w.next(), isFalse);
    expect(w.current, 0);
    w.markValid(0, true);
    expect(w.next(), isTrue);
    expect(w.current, 1);
  });
}
