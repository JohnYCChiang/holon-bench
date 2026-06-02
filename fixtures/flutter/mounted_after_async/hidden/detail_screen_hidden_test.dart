import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mounted_after_async/screens/detail_screen.dart';

void main() {
  testWidgets('hidden success and error states still render while mounted', (tester) async {
    await tester.pumpWidget(DetailScreen(key: UniqueKey(), load: () async => 'Loaded'));
    await tester.pump();
    expect(find.text('Loaded'), findsOneWidget);

    await tester.pumpWidget(DetailScreen(key: UniqueKey(), load: () async => throw StateError('boom')));
    await tester.pump();
    expect(find.text('Error'), findsOneWidget);
  });

  testWidgets('hidden error completion after dispose does not call setState', (tester) async {
    final completer = Completer<String>();
    await tester.pumpWidget(DetailScreen(load: () => completer.future));
    expect(find.text('Loading'), findsOneWidget);

    await tester.pumpWidget(const SizedBox.shrink());
    completer.completeError(StateError('late failure'));
    await tester.pump();

    expect(tester.takeException(), isNull);
  });
}
