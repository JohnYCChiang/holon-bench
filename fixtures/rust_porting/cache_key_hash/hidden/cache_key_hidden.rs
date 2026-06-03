use cache_key_hash::cache_key;
use serde_json::json;
use std::process::Command;

fn python_key(payload: &str) -> String {
    let script = concat!(env!("CARGO_MANIFEST_DIR"), "/../python/reference.py");
    let output = Command::new("python3")
        .args([script, payload])
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "python reference failed: {output:?}"
    );
    String::from_utf8(output.stdout).unwrap().trim().to_string()
}

#[test]
fn hidden_matches_python_for_deeply_nested_mixed_payload() {
    let payload = json!({
        "query": " rust ",
        "options": {
            "tags": [" x ", {"k": " y "}],
            "limit": 4
        },
        "meta": {
            "b": " two ",
            "a": " one "
        }
    });

    assert_eq!(
        cache_key(&payload),
        python_key(
            r#"{"query":" rust ","options":{"tags":[" x ",{"k":" y "}],"limit":4},"meta":{"b":" two ","a":" one "}}"#
        )
    );
}
