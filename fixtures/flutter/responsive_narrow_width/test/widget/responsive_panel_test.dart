import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:responsive_narrow_width/widgets/responsive_panel.dart';

void main() {
  testWidgets('uses stacked layout at narrow width', (tester) async {
    await tester.binding.setSurfaceSize(const Size(320, 640));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(const ResponsivePanel());
    final filters = tester.getTopLeft(find.text('Filters'));
    final results = tester.getTopLeft(find.text('Results'));

    expect(results.dy, greaterThan(filters.dy));
    expect(tester.takeException(), isNull);
  });

  testWidgets('keeps side by side layout at desktop width', (tester) async {
    await tester.binding.setSurfaceSize(const Size(900, 640));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(const ResponsivePanel());
    final filters = tester.getTopLeft(find.text('Filters'));
    final results = tester.getTopLeft(find.text('Results'));

    expect(results.dx, greaterThan(filters.dx));
  });
}
