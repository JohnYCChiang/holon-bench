import 'dart:async';

import 'package:async_search_dedupe/state/search_controller.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('deduplicates concurrent identical searches only while in flight', () async {
    var calls = 0;
    final gate = Completer<List<String>>();
    final controller = SearchController((query) {
      calls++;
      return gate.future;
    });

    final first = controller.search('abc');
    final second = controller.search('abc');
    expect(calls, 1);

    gate.complete(['abc']);
    expect(await first, ['abc']);
    expect(await second, ['abc']);

    final controller2 = SearchController((query) async {
      calls++;
      return [query];
    });
    expect(await controller2.search('abc'), ['abc']);
    expect(calls, 2);
  });
}
