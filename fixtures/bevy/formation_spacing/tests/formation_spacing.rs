use formation_spacing::formation::slot_offsets;

#[test]
fn odd_count_is_centered() {
    assert_eq!(slot_offsets(3, 2.0), vec![-2.0, 0.0, 2.0]);
}

#[test]
fn even_count_is_centered() {
    assert_eq!(slot_offsets(2, 2.0), vec![-1.0, 1.0]);
}
