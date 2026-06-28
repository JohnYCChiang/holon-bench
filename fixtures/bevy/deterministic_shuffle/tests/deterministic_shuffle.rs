use deterministic_shuffle::shuffle::shuffle;

#[test]
fn matches_reference_for_seed() {
    let mut a: Vec<u32> = (0..8).collect();
    shuffle(&mut a, 42);
    assert_eq!(a, vec![0, 3, 6, 7, 4, 5, 2, 1]);
}

#[test]
fn preserves_all_elements() {
    let mut a: Vec<u32> = (0..16).collect();
    shuffle(&mut a, 777);
    a.sort();
    let expected: Vec<u32> = (0..16).collect();
    assert_eq!(a, expected);
}
