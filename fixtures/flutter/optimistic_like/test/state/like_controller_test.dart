import 'package:flutter_test/flutter_test.dart';
import 'package:optimistic_like/state/like_controller.dart';

void main() {
  test('a successful commit keeps the toggled state', () async {
    final c = LikeController(
      liked: false,
      count: 10,
      commit: (_) async {},
    );
    final ok = await c.toggle();
    expect(ok, isTrue);
    expect(c.liked, isTrue);
    expect(c.count, 11);
  });
}
