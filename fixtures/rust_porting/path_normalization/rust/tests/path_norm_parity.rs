use path_normalization::path_norm::normalize_path;
use std::process::Command;

fn python(path: &str) -> String {
    let script = concat!(env!("CARGO_MANIFEST_DIR"), "/../python/reference.py");
    let output = Command::new("python3").args([script, path]).output().unwrap();
    assert!(output.status.success());
    String::from_utf8(output.stdout).unwrap().trim().to_string()
}

fn rust(path: &str) -> String {
    match normalize_path(path) {
        Ok(path) => format!("ok={path}"),
        Err(code) => format!("error={code}"),
    }
}

#[test]
fn normalizes_like_python_reference() {
    for path in ["src/./tool.py", r"src\\tool.py", "src//nested/file.py", "../secret"] {
        assert_eq!(rust(path), python(path), "path={path}");
    }
}
