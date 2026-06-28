/// Tracks which expansion panels are open, optionally as a single-open
/// accordion.
class ExpansionState {
  final bool singleOpen;
  final Set<int> _open = <int>{};

  ExpansionState({this.singleOpen = false});

  Set<int> get openPanels => Set.unmodifiable(_open);
  bool isOpen(int index) => _open.contains(index);

  void toggle(int index) {
    _open.add(index); // BUG: never closes and ignores single-open mode
  }

  void collapseAll() => _open.clear();
}
