import 'dart:io';

/// Copies text to the system clipboard. Currently shells out via dart:io,
/// which pulls dart:io into the web build. It must depend on an injected
/// ClipboardSink boundary instead.
class ClipboardService {
  final List<String> _history = [];

  void copy(String text) {
    _history.add(text);
    Process.runSync('xclip', const ['-selection', 'clipboard']);
    File('clipboard.txt').writeAsStringSync(text);
  }

  List<String> get history => List.unmodifiable(_history);
}
