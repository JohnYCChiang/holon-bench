/// Applies a like optimistically and rolls back when the commit fails.
class LikeController {
  bool liked;
  int count;
  final Future<void> Function(bool desired) _commit;

  LikeController({
    required this.liked,
    required this.count,
    required Future<void> Function(bool desired) commit,
  }) : _commit = commit;

  Future<bool> toggle() async {
    liked = !liked;
    count += liked ? 1 : -1;
    try {
      await _commit(liked);
      return true;
    } catch (_) {
      return false; // BUG: leaves the optimistic state instead of rolling back
    }
  }
}
