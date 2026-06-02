import 'dart:io';

class SaveStore {
  Future<void> save(String slot, String value) async {
    await File('$slot.save').writeAsString(value);
  }

  Future<String> load(String slot) {
    return File('$slot.save').readAsString();
  }
}
