use cache_manifest::manifest::{summarize, Entry};
use std::process::Command;

fn python(payload: &str) -> String {
    let script = concat!(env!("CARGO_MANIFEST_DIR"), "/../python/reference.py");
    let output = Command::new("python3").args([script, payload]).output().unwrap();
    assert!(output.status.success());
    String::from_utf8(output.stdout).unwrap().trim().to_string()
}

#[test]
fn summarizes_manifest_like_python_reference() {
    let entries = vec![
        Entry { path: "b.json".to_string(), bytes: 7, stale: true },
        Entry { path: "a.json".to_string(), bytes: 5, stale: false },
    ];
    let payload = r#"[{"path":"b.json","bytes":7,"stale":true},{"path":"a.json","bytes":5,"stale":false}]"#;
    assert_eq!(summarize(&entries), python(payload));
}
