/// Most-recent-first search history with case-insensitive dedupe and a cap.
class SearchHistory {
  final int maxEntries;
  final List<String> _entries = <String>[];

  SearchHistory({this.maxEntries = 5}) : assert(maxEntries > 0);

  List<String> get entries => List.unmodifiable(_entries);

  void record(String query) {
    _entries.add(query); // BUG: no trim, no dedupe, no cap, wrong order
  }

  void clear() => _entries.clear();
}
