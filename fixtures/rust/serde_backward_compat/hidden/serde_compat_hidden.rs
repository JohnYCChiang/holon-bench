use serde_backward_compat::ToolResult;

#[test]
fn hidden_missing_detail_defaults_to_none_for_multiple_statuses() {
    for raw in [
        r#"{"id":"job-ok","status":"ok"}"#,
        r#"{"id":"job-fail","status":"failed"}"#,
    ] {
        let result: ToolResult = serde_json::from_str(raw).expect("old JSON without detail loads");
        assert_eq!(result.detail, None);
        assert!(serde_json::to_value(&result).unwrap().get("detail").is_none());
    }
}

#[test]
fn hidden_detail_round_trips_without_renaming_existing_fields() {
    let raw = r#"{"id":"job-3","status":"failed","detail":"disk full"}"#;
    let result: ToolResult = serde_json::from_str(raw).expect("new JSON with detail loads");
    assert_eq!(result.id, "job-3");
    assert_eq!(result.status, "failed");
    assert_eq!(result.detail.as_deref(), Some("disk full"));

    let serialized = serde_json::to_value(&result).unwrap();
    assert_eq!(serialized["id"], "job-3");
    assert_eq!(serialized["status"], "failed");
    assert_eq!(serialized["detail"], "disk full");
}
