typedef SearchClient = Future<List<String>> Function(String query);

class SearchController {
  SearchController(this._client);

  final SearchClient _client;

  Future<List<String>> search(String query) {
    return _client(query);
  }
}
