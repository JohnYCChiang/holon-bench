import 'package:flutter_test/flutter_test.dart';
import 'package:clipboard_trap/clipboard/clipboard_service.dart';
import 'package:clipboard_trap/clipboard/clipboard_sink.dart';

class MemoryClipboard implements ClipboardSink {
  final List<String> writes = [];
  @override
  void setText(String text) => writes.add(text);
}

void main() {
  test('clipboard service writes through the injected sink', () {
    final sink = MemoryClipboard();
    final service = ClipboardService(sink);

    service.copy('hello');
    service.copy('world');

    expect(sink.writes, ['hello', 'world']);
    expect(service.history, ['hello', 'world']);
  });
}
