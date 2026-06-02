import 'package:flutter/material.dart';
import 'package:domain_validation/widgets/form_view.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('preserves displayed validation message', (tester) async {
    await tester.pumpWidget(const RegistrationForm());
    await tester.enterText(find.byKey(const Key('email')), 'bad');
    await tester.tap(find.text('Submit'));
    await tester.pump();

    expect(find.text('Enter a valid email'), findsOneWidget);
  });
}
