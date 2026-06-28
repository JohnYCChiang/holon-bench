import 'dart:io';

/// Records crash messages. Currently writes straight to a dart:io file, which
/// pulls dart:io into the web build. It must depend on an injected LogSink.
class CrashLogger {
  final List<String> _buffer = [];

  void log(String message) {
    _buffer.add(message);
    stderr.writeln(message);
    File('crash.log').writeAsStringSync('$message\n', mode: FileMode.append);
  }

  List<String> get entries => List.unmodifiable(_buffer);
}
