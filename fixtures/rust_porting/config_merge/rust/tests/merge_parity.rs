use config_merge::merge::merge_config;
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
fn merges_config_like_python_reference() {
    let text = "{\"a\":1,\"b\":{\"x\":1,\"y\":2},\"c\":[1,2]}\n{\"b\":{\"y\":3,\"z\":4},\"c\":[9],\"d\":5}";
    assert_eq!(merge_config(text), python(text));
}
