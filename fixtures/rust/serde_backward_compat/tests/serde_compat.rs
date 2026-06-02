use serde_backward_compat::ToolResult;

#[test]
fn serde_compat_preserves_old_json_and_omits_absent_detail() {
    let old: ToolResult =
        serde_json::from_str(include_str!("fixtures/old_result.json")).expect("old data loads");
    assert_eq!(old.detail, None);

    let without_detail = serde_json::to_value(&old).unwrap();
    assert!(without_detail.get("detail").is_none());

    let with_detail = ToolResult {
        id: "job-2".to_string(),
        status: "failed".to_string(),
        detail: Some("network error".to_string()),
    };
    assert_eq!(
        serde_json::to_value(with_detail).unwrap()["detail"],
        "network error"
    );
}
