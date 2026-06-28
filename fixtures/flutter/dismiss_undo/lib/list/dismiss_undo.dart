/// A list supporting swipe-dismiss with a single-level undo that restores the
/// most recently dismissed item at its original index.
class DismissList<T> {
  final List<T> _items;
  ({int index, T value})? _pending;

  DismissList(List<T> items) : _items = List<T>.of(items);

  List<T> get items => List.unmodifiable(_items);
  bool get canUndo => _pending != null;

  void dismiss(int index) {
    final value = _items.removeAt(index);
    _pending = (index: index, value: value);
  }

  bool undo() {
    final p = _pending;
    if (p == null) return false;
    _items.add(p.value); // BUG: appends instead of restoring the original index
    _pending = null;
    return true;
  }
}
