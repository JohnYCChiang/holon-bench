use jsonl_parser::jsonl::parse_jsonl;
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

fn rust(text: &str) -> String {
    let (records, errors) = parse_jsonl(text);
    let records = records.join(",");
    let errors = errors.iter().map(|v| v.to_string()).collect::<Vec<_>>().join(",");
    format!("records={records};errors={errors}")
}

#[test]
fn parses_jsonl_like_python_reference() {
    let text = "{\"id\":1}\n\nnot-json\n{\"id\":2}\n{\"name\":\"missing\"}\n";
    assert_eq!(rust(text), python(text));
}
