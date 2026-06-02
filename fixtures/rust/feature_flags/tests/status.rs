use feature_flags::status::format_status;

#[test]
fn format_status_respects_feature_flag() {
    let output = format_status(true, "cache warm");
    if cfg!(feature = "verbose") {
        assert_eq!(output, "ok=true;detail=cache warm");
    } else {
        assert_eq!(output, "ok=true");
    }
}
