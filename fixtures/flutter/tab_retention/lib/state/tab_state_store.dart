/// Retains a per-tab scroll offset across tab switches.
class TabStateStore {
  final int tabCount;
  int _active;
  final Map<int, double> _offsets = <int, double>{};

  TabStateStore(this.tabCount, {int initial = 0})
      : assert(tabCount > 0),
        _active = initial;

  int get active => _active;
  double offsetOf(int tab) => _offsets[tab] ?? 0.0;
  double get activeOffset => offsetOf(_active);

  void saveOffset(double offset) {
    _offsets[0] = offset; // BUG: always writes tab 0 instead of the active tab
  }

  bool switchTo(int tab) {
    _active = tab; // BUG: no range validation
    return true;
  }
}
