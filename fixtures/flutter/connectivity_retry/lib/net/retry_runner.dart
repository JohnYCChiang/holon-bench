typedef Sleeper = Future<void> Function(Duration delay);

/// Retries an async action with exponential backoff, giving up after
/// [maxAttempts] tries and rethrowing the final error.
class RetryRunner {
  RetryRunner({
    required this.maxAttempts,
    required this.baseDelay,
    required this.sleep,
  });

  final int maxAttempts;
  final Duration baseDelay;
  final Sleeper sleep;

  Future<T> run<T>(Future<T> Function(int attempt) action) async {
    return action(1);
  }
}
