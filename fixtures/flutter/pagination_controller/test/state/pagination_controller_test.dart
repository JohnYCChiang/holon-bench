import 'package:flutter_test/flutter_test.dart';
import 'package:pagination_controller/state/pagination_controller.dart';

void main() {
  test('loads successive pages and accumulates items', () async {
    final pages = {
      0: ['a', 'b'],
      1: ['c', 'd'],
    };
    final controller = PaginationController(
      pageSize: 2,
      fetchPage: (page) async => pages[page] ?? <String>[],
    );

    await controller.loadNextPage();
    expect(controller.items, ['a', 'b']);

    await controller.loadNextPage();
    expect(controller.items, ['a', 'b', 'c', 'd']);
  });
}
