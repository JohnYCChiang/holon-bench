typedef Sender = Future<bool> Function(String message);

class OfflineQueue {
  OfflineQueue(this._sender);

  final Sender _sender;
  final List<String> _pending = [];

  List<String> get pending => List.unmodifiable(_pending);

  void add(String message) {
    _pending.add(message);
  }

  Future<void> flush() async {
    for (final message in List<String>.from(_pending)) {
      await _sender(message);
      _pending.remove(message);
    }
  }
}
