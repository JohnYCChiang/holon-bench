use base32_encode::base32::b32encode;
use std::io::Write;
use std::process::{Command, Stdio};

fn python(text: &str) -> String {
    let script = concat!(env!("CARGO_MANIFEST_DIR"), "/../python/reference.py");
    let mut child = Command::new("python3")
        .arg(script)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .unwrap();
    child.stdin.as_mut().unwrap().write_all(text.as_bytes()).unwrap();
    let output = child.wait_with_output().unwrap();
    assert!(output.status.success());
    String::from_utf8(output.stdout).unwrap().trim().to_string()
}

#[test]
fn encodes_like_python_reference() {
    let text = "hi";
    assert_eq!(b32encode(text), python(text));
}