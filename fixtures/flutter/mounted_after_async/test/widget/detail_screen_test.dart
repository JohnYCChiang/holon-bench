import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mounted_after_async/screens/detail_screen.dart';

void main() {
  testWidgets('does not call setState after dispose', (tester) async {
    final completer = Completer<String>();
    await tester.pumpWidget(DetailScreen(load: () => completer.future));
    expect(find.text('Loading'), findsOneWidget);

    await tester.pumpWidget(const SizedBox.shrink());
    completer.complete('Done');
    await tester.pump();

    expect(tester.takeException(), isNull);
  });
}
