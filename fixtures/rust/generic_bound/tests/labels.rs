use generic_bound::labels::join_labels;

#[test]
fn accepts_borrowed_string_like_values() {
    let labels = ["beta", "alpha"];
    assert_eq!(join_labels(labels.iter()), "beta,alpha");
}

#[test]
fn accepts_owned_strings_without_api_split() {
    let labels = vec!["one".to_string(), "two".to_string()];
    assert_eq!(join_labels(labels.iter()), "one,two");
}
