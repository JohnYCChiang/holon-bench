use exit_classifier::exit_class::classify_exit;
use std::process::Command;

fn python(code: i32) -> String {
    let script = concat!(env!("CARGO_MANIFEST_DIR"), "/../python/reference.py");
    let output = Command::new("python3").args([script, &code.to_string()]).output().unwrap();
    assert!(output.status.success());
    String::from_utf8(output.stdout).unwrap().trim().to_string()
}

fn rust(code: i32) -> String {
    let (kind, retryable) = classify_exit(code);
    format!("{kind}|{retryable}")
}

#[test]
fn classifies_exit_codes_like_python_reference() {
    for code in [0, 1, 2, -15, 124] {
        assert_eq!(rust(code), python(code), "code={code}");
    }
}
