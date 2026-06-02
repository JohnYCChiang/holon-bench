use stderr_parser::stderr_parser::parse_stderr;
use std::io::Write;
use std::process::{Command, Stdio};

fn python(text: &str) -> String {
    let script = concat!(env!("CARGO_MANIFEST_DIR"), "/../python/reference.py");
    let mut child = Command::new("python3").arg(script).stdin(Stdio::piped()).stdout(Stdio::piped()).spawn().unwrap();
    child.stdin.as_mut().unwrap().write_all(text.as_bytes()).unwrap();
    let output = child.wait_with_output().unwrap();
    assert!(output.status.success());
    String::from_utf8(output.stdout).unwrap().trim().to_string()
}

#[test]
fn parses_stderr_like_python_reference() {
    let text = "noise\nWARN: slow\nERROR: failed to parse\nWARN: retry\nERROR: bad input\n";
    assert_eq!(parse_stderr(text), python(text));
}
