typedef Clock = DateTime Function();

/// Suppresses a repeated identical message shown within [window] of the last
/// time that same message was actually displayed.
class SnackbarDispatcher {
  SnackbarDispatcher({required this.now, required this.window});

  final Clock now;
  final Duration window;

  /// Returns true when the message is actually shown.
  bool show(String message) {
    return true;
  }
}
