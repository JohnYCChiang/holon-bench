enum ThemeChoice { light, dark, system }

abstract class KeyValueStore {
  Future<String?> read(String key);
  Future<void> write(String key, String value);
}

/// Persists the selected theme and cycles light -> dark -> system.
class ThemeStore {
  ThemeStore(this._store);

  static const _key = 'theme';
  final KeyValueStore _store;

  ThemeChoice current = ThemeChoice.system;

  Future<void> load() async {
    // TODO: read persisted value.
  }

  Future<void> cycle() async {
    final order = ThemeChoice.values;
    current = order[(current.index + 1) % order.length];
  }
}
