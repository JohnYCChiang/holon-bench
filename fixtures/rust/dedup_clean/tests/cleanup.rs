use dedup_clean::cleanup::clean;

#[test]
fn removes_then_dedups() {
    let mut v = vec![1, -2, 1];
    clean(&mut v);
    assert_eq!(v, vec![1]);
}

#[test]
fn dedups_consecutive() {
    let mut v = vec![1, 2, 2, 3];
    clean(&mut v);
    assert_eq!(v, vec![1, 2, 3]);
}
