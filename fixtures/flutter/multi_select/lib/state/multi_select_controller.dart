import 'dart:collection';

/// Tracks a multi-selection over item ids, preserving selection order.
class SelectionController {
  final LinkedHashSet<String> _selected = LinkedHashSet<String>();

  Set<String> get selected => Set.unmodifiable(_selected);
  List<String> get selectedIds => List.unmodifiable(_selected);
  int get count => _selected.length;
  bool isSelected(String id) => _selected.contains(id);

  void toggle(String id) {
    _selected.add(id); // BUG: never removes an already-selected id
  }

  void selectAll(Iterable<String> ids) {
    _selected
      ..clear() // BUG: discards the existing selection and its order
      ..addAll(ids);
  }

  void clear() => _selected.clear();
}
