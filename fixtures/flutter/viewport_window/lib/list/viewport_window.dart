/// Computes the inclusive index range of items intersecting a viewport for a
/// uniformly-sized virtualized list.
({int firstIndex, int lastIndex}) visibleRange({
  required double scrollOffset,
  required double viewportExtent,
  required double itemExtent,
  required int itemCount,
  int overscan = 0,
}) {
  final first = (scrollOffset / itemExtent).floor();
  final last = first + (viewportExtent / itemExtent).floor();
  return (firstIndex: first, lastIndex: last); // BUG: no overscan/clamp/empty
}
