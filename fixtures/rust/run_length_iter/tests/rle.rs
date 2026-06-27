use run_length_iter::rle::RunLength;

#[test]
fn expands_runs_in_order() {
    let s: String = RunLength::new(vec![('a', 2), ('b', 1), ('c', 3)]).collect();
    assert_eq!(s, "aabccc");
}

#[test]
fn empty_runs_yield_nothing() {
    let s: String = RunLength::new(vec![]).collect();
    assert_eq!(s, "");
}
