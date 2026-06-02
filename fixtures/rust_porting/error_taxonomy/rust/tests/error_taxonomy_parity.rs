use error_taxonomy::error_taxonomy::classify;
use std::process::Command;

fn python(kind: &str) -> String {
    let script = concat!(env!("CARGO_MANIFEST_DIR"), "/../python/reference.py");
    let output = Command::new("python3").args([script, kind]).output().unwrap();
    assert!(output.status.success());
    String::from_utf8(output.stdout).unwrap().trim().to_string()
}

fn rust(kind: &str) -> String {
    let error = classify(kind);
    format!("{}|{}", error.code, error.retryable)
}

#[test]
fn matches_python_error_taxonomy() {
    for kind in ["timeout", "rate", "validation", "not_found", "weird"] {
        assert_eq!(rust(kind), python(kind), "kind={kind}");
    }
}
