import 'package:dart_io_web_trap/platform/file_selector.dart';
import 'package:dart_io_web_trap/services/file_picker.dart';
import 'package:flutter_test/flutter_test.dart';

class FakeFileSelector implements FileSelector {
  @override
  Future<SelectedFile?> pick(String path) async {
    if (path == 'missing') {
      return null;
    }
    return SelectedFile(path);
  }
}

void main() {
  test('file picker uses platform abstraction', () async {
    final picker = ConfigFilePicker(FakeFileSelector());

    expect((await picker.pickConfigFile('settings.json'))?.path, 'settings.json');
    expect(await picker.pickConfigFile('missing'), isNull);
  });
}
