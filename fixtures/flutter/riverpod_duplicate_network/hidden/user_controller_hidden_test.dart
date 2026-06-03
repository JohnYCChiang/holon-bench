import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:riverpod_duplicate_network/services/user_api.dart';
import 'package:riverpod_duplicate_network/state/user_controller.dart';

class PendingUserApi implements UserApi {
  int calls = 0;
  final completer = Completer<String>();

  @override
  Future<String> fetchUser() {
    calls++;
    return completer.future;
  }
}

void main() {
  test('hidden coalesces pending load calls until the request completes',
      () async {
    final api = PendingUserApi();
    final controller = UserController(api);

    final first = controller.load();
    final second = controller.load();
    final third = controller.load();

    expect(api.calls, 1);
    api.completer.complete('user-1');

    expect(await Future.wait([first, second, third]),
        ['user-1', 'user-1', 'user-1']);
  });
}
