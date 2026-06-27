use rolling_checksum::checksum;

#[test]
fn long_input_wraps_without_panicking() {
    assert_eq!(checksum(b"holon-bench-overflow-checksum-input"), 1_621_673_765);
}
