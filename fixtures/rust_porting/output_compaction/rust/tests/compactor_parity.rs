use output_compaction::compactor::compact;
use std::io::Write;
use std::process::{Command, Stdio};

fn python(text: &str, limit: usize) -> String {
    let script = concat!(env!("CARGO_MANIFEST_DIR"), "/../python/reference.py");
    let mut child = Command::new("python3")
        .args([script, &limit.to_string()])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .unwrap();
    child.stdin.as_mut().unwrap().write_all(text.as_bytes()).unwrap();
    let output = child.wait_with_output().unwrap();
    assert!(output.status.success());
    String::from_utf8(output.stdout).unwrap().trim().to_string()
}

fn rust(text: &str, limit: usize) -> String {
    let (omitted, body) = compact(text, limit);
    format!("omitted={omitted};body={body}")
}

#[test]
fn compacts_like_python_reference() {
    assert_eq!(rust("a\nb\nc\nd\n", 2), python("a\nb\nc\nd\n", 2));
    assert_eq!(rust("a\nb\n", 3), python("a\nb\n", 3));
}
