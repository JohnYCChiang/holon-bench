use pathlib_to_walkdir::scan_files;
use serde_json::Value;
use std::fs;
use std::process::Command;
use std::time::{SystemTime, UNIX_EPOCH};

#[test]
fn scanner_matches_python_filtering_and_order() {
    let root = std::env::temp_dir().join(format!(
        "holon-rs-port-scanner-{}",
        SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos()
    ));
    fs::create_dir_all(root.join(".cache")).unwrap();
    fs::create_dir_all(root.join("nested")).unwrap();
    fs::write(root.join("z.txt"), "z").unwrap();
    fs::write(root.join("nested/a.txt"), "a").unwrap();
    fs::write(root.join("ignored.log"), "log").unwrap();
    fs::write(root.join(".cache/secret.txt"), "hidden").unwrap();

    let rust = serde_json::to_value(scan_files(&root, ".log")).unwrap();
    let script = concat!(env!("CARGO_MANIFEST_DIR"), "/../python/reference.py");
    let output = Command::new("python3")
        .args([script, root.to_str().unwrap(), ".log"])
        .output()
        .unwrap();
    let python: Value = serde_json::from_slice(&output.stdout).unwrap();
    fs::remove_dir_all(&root).unwrap();

    assert_eq!(rust, python);
    assert_eq!(rust["files"], serde_json::json!(["nested/a.txt", "z.txt"]));
}
