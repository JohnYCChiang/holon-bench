use schema_structs::schema::{run, ToolRequest};
use serde_json::Value;
use std::process::Command;

fn python(payload: &str) -> Value {
    let script = concat!(env!("CARGO_MANIFEST_DIR"), "/../python/reference.py");
    let output = Command::new("python3").args([script, payload]).output().unwrap();
    assert!(output.status.success());
    serde_json::from_slice(&output.stdout).unwrap()
}

#[test]
fn valid_request_serializes_like_python_reference() {
    let payload = r#"{"root":"src","include_hidden":true}"#;
    let request: ToolRequest = serde_json::from_str(payload).unwrap();
    assert_eq!(serde_json::to_value(run(request)).unwrap(), python(payload));
}

#[test]
fn defaults_optional_field_like_python_reference() {
    let payload = r#"{"root":"src"}"#;
    let request: ToolRequest = serde_json::from_str(payload).unwrap();
    assert_eq!(serde_json::to_value(run(request)).unwrap(), python(payload));
}

#[test]
fn rejects_unknown_fields_as_the_python_contract_does() {
    let payload = r#"{"root":"src","debug":true}"#;
    assert!(serde_json::from_str::<ToolRequest>(payload).is_err());
    assert_eq!(python(payload)["error"]["code"], "invalid_request");
}
