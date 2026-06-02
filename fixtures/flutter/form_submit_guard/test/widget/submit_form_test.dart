import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:form_submit_guard/widgets/submit_form.dart';

void main() {
  testWidgets('ignores duplicate taps while submit is in flight', (tester) async {
    var calls = 0;
    final gate = Completer<void>();
    await tester.pumpWidget(SubmitForm(onSubmit: () {
      calls++;
      return gate.future;
    }));

    await tester.tap(find.byType(ElevatedButton));
    await tester.pump();
    await tester.tap(find.byType(ElevatedButton));
    await tester.pump();

    expect(calls, 1);
    expect(find.text('Saving'), findsOneWidget);
    gate.complete();
    await tester.pump();
    expect(find.text('Save'), findsOneWidget);
  });
}
