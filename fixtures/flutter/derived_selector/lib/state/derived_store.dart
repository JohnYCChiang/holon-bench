/// Holds a raw value and exposes a derived "bucket" (value ~/ 10). Listeners
/// should be notified only when the derived bucket actually changes.
class DerivedStore {
  DerivedStore(this._value);

  int _value;
  final List<void Function(int bucket)> _listeners = [];

  int get value => _value;
  int get bucket => _value ~/ 10;

  void listen(void Function(int bucket) listener) {
    _listeners.add(listener);
  }

  void set(int next) {
    _value = next;
    for (final l in _listeners) {
      l(bucket);
    }
  }
}
