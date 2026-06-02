import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:layout_overflow_card/widgets/profile_card.dart';

void main() {
  testWidgets('stacks at narrow width without overflow', (tester) async {
    await tester.binding.setSurfaceSize(const Size(260, 640));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(const ProfileCard());

    final icon = tester.getTopLeft(find.byIcon(Icons.person));
    final text = tester.getTopLeft(find.text('Very long profile name that must remain visible'));
    expect(text.dy, greaterThan(icon.dy));
    expect(tester.takeException(), isNull);
  });

  testWidgets('keeps horizontal layout on desktop width', (tester) async {
    await tester.binding.setSurfaceSize(const Size(900, 640));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(const ProfileCard());

    final icon = tester.getTopLeft(find.byIcon(Icons.person));
    final text = tester.getTopLeft(find.text('Very long profile name that must remain visible'));
    expect(text.dx, greaterThan(icon.dx));
  });
}
