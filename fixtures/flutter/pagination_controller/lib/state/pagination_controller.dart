typedef PageFetcher = Future<List<String>> Function(int page);

/// Loads list data page by page and accumulates the results.
class PaginationController {
  PaginationController({required this.pageSize, required this.fetchPage});

  final int pageSize;
  final PageFetcher fetchPage;

  final List<String> items = [];
  bool hasMore = true;

  Future<void> loadNextPage() async {
    final page = await fetchPage(0);
    items.addAll(page);
  }
}
