import 'package:flutter_test/flutter_test.dart';
import 'package:web_log_sink_trap/logging/crash_logger.dart';
import 'package:web_log_sink_trap/logging/log_sink.dart';

class MemorySink implements LogSink {
  final List<String> lines = [];
  @override
  void writeLine(String line) => lines.add(line);
}

void main() {
  test('crash logger writes through the injected sink', () {
    final sink = MemorySink();
    final logger = CrashLogger(sink);

    logger.log('boom');
    logger.log('bang');

    expect(sink.lines, ['boom', 'bang']);
    expect(logger.entries, ['boom', 'bang']);
  });
}
