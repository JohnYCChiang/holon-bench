/// Returns a new list with the element at [oldIndex] moved to the position
/// reported by a Flutter ReorderableListView `onReorder` callback.
List<String> reorder(List<String> items, int oldIndex, int newIndex) {
  final copy = List<String>.from(items);
  final moved = copy.removeAt(oldIndex);
  copy.insert(newIndex, moved);
  return copy;
}
