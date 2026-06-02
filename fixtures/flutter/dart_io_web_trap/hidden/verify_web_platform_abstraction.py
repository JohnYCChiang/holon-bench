from pathlib import Path
import re
import sys


IMPORT_RE = re.compile(r"^\s*import\s+['\"]([^'\"]+)['\"]", re.MULTILINE)
EXPORT_RE = re.compile(r"^\s*export\s+['\"]([^'\"]+)['\"]", re.MULTILINE)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def dart_imports(text: str) -> set[str]:
    return set(IMPORT_RE.findall(text))


def dart_exports(text: str) -> set[str]:
    return set(EXPORT_RE.findall(text))


def main() -> int:
    root = Path(".")
    lib = root / "lib"
    errors: list[str] = []

    service = lib / "services" / "file_picker.dart"
    if not service.exists():
        errors.append("missing lib/services/file_picker.dart")
    else:
        service_text = read(service)
        service_imports = dart_imports(service_text)
        if "dart:io" in service_imports:
            errors.append("service file must not import dart:io")
        if re.search(r"\bFile\s*\(", service_text):
            errors.append("service file must not directly construct File")
        if "FileSelector" not in service_text or "ConfigFilePicker" not in service_text:
            errors.append("service file must expose an injectable ConfigFilePicker/FileSelector boundary")

    boundary = lib / "platform" / "file_selector.dart"
    if not boundary.exists():
        errors.append("missing lib/platform/file_selector.dart")
    else:
        boundary_text = read(boundary)
        if "dart:io" in dart_imports(boundary_text):
            errors.append("platform boundary file must not import dart:io")
        if "FileSelector" not in boundary_text or "SelectedFile" not in boundary_text:
            errors.append("platform boundary must define FileSelector and SelectedFile")

    for path in lib.rglob("*.dart"):
        text = read(path)
        imports = dart_imports(text)
        rel = path.relative_to(root).as_posix()

        if path.name.endswith("_web.dart") and "dart:io" in imports:
            errors.append(f"web implementation imports dart:io: {rel}")

        if "dart:io" in imports:
            allowed_native_impl = path.stem.endswith(("_io", "_native", "_desktop"))
            if not allowed_native_impl:
                errors.append(f"dart:io is not isolated to a native implementation: {rel}")

        if path.name.endswith("_io.dart"):
            exports = dart_exports(text)
            if "dart:io" in exports:
                errors.append(f"native implementation must not re-export dart:io: {rel}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
