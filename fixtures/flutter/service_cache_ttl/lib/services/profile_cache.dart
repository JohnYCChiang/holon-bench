typedef FetchProfile = Future<String> Function();
typedef Clock = DateTime Function();

class ProfileCache {
  ProfileCache({required this.fetch, required this.now, required this.ttl});

  final FetchProfile fetch;
  final Clock now;
  final Duration ttl;

  String? _cached;

  Future<String> get() async {
    _cached ??= await fetch();
    return _cached!;
  }
}
