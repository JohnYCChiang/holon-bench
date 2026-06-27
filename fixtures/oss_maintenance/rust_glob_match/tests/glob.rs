use glob_match::matches;

#[test]
fn star_matches_empty_run() {
    assert!(matches("a*", "a"));
}
