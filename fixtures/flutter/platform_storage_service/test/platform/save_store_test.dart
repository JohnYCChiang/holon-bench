import 'package:flutter_test/flutter_test.dart';
import 'package:platform_storage_service/platform/save_store.dart';

class MemoryStorage implements Storage {
  final values = <String, String>{};

  @override
  Future<void> write(String key, String value) async {
    values[key] = value;
  }

  @override
  Future<String> read(String key) async => values[key]!;
}

void main() {
  test('save store uses injected storage', () async {
    final storage = MemoryStorage();
    final store = SaveStore(storage);

    await store.save('slot1', 'level=3');

    expect(await store.load('slot1'), 'level=3');
  });
}
