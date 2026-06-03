import 'package:flutter_test/flutter_test.dart';
import 'package:riverpod_duplicate_network/services/user_api.dart';
import 'package:riverpod_duplicate_network/state/user_controller.dart';

class FailingThenRecoveringApi implements UserApi {
  int calls = 0;

  @override
  Future<String> fetchUser() async {
    calls++;
    if (calls == 1) {
      throw StateError('temporary failure');
    }
    return 'user-$calls';
  }
}

void main() {
  test('mutation clears failed in-flight load so the next load can retry',
      () async {
    final api = FailingThenRecoveringApi();
    final controller = UserController(api);

    await expectLater(controller.load(), throwsStateError);
    expect(await controller.load(), 'user-2');
    expect(api.calls, 2);
  });
}
