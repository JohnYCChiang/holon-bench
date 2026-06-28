import 'package:flutter_test/flutter_test.dart';
import 'package:theme_mode_store/settings/theme_store.dart';

class MapStore implements KeyValueStore {
  final values = <String, String>{};
  @override
  Future<String?> read(String key) async => values[key];
  @override
  Future<void> write(String key, String value) async => values[key] = value;
}

void main() {
  test('cycling persists the new choice and reloads it', () async {
    final backing = MapStore();
    final store = ThemeStore(backing);

    await store.cycle(); // system -> light
    expect(store.current, ThemeChoice.light);

    final reopened = ThemeStore(backing);
    await reopened.load();
    expect(reopened.current, ThemeChoice.light);
  });
}
