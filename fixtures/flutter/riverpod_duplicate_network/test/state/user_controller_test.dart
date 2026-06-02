import 'package:flutter_test/flutter_test.dart';
import 'package:riverpod_duplicate_network/services/user_api.dart';
import 'package:riverpod_duplicate_network/state/user_controller.dart';

void main() {
  test('coalesces duplicate load calls but preserves manual refresh', () async {
    final api = CountingUserApi();
    final controller = UserController(api);

    final values = await Future.wait([controller.load(), controller.load()]);
    expect(values, ['user-1', 'user-1']);
    expect(api.calls, 1);

    expect(await controller.refresh(), 'user-2');
    expect(api.calls, 2);
  });
}
