use cache_key_hash::cache_key;
use serde_json::json;
use std::process::Command;

fn python_key(payload: &str) -> String {
    let script = concat!(env!("CARGO_MANIFEST_DIR"), "/../python/reference.py");
    let output = Command::new("python3").args([script, payload]).output().unwrap();
    assert!(output.status.success());
    String::from_utf8(output.stdout).unwrap().trim().to_string()
}

#[test]
fn normalizes_nested_keys_and_strings_like_python() {
    let payload = json!({"query": "  rust  ", "options": {"limit": 4, "tags": [" ai ", "tool"]}});
    assert_eq!(
        cache_key(&payload),
        python_key(r#"{"options":{"tags":[" ai ","tool"],"limit":4},"query":"  rust  "}"#)
    );
}

#[test]
fn version_salt_is_part_of_the_golden_hash() {
    let payload = json!({"query": "rust", "options": {"limit": 4, "tags": ["ai", "tool"]}});
    assert_eq!(
        cache_key(&payload),
        "905f47b1fc62eea5af83cb9e944367ae008ecbb2436c75229c2af74035d63ff4"
    );
}
