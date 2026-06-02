import 'dart:io';

class PickedFile {
  PickedFile(this.path);

  final String path;
}

Future<PickedFile?> pickConfigFile(String path) async {
  if (!File(path).existsSync()) {
    return null;
  }
  return PickedFile(path);
}
