use percentage_newtype::percentage::{OutOfRange, Percentage};

#[test]
fn accepts_in_range() {
    assert_eq!(Percentage::new(50).map(|p| p.value()), Ok(50));
}

#[test]
fn accepts_boundary_100() {
    assert_eq!(Percentage::new(100).map(|p| p.value()), Ok(100));
}

#[test]
fn rejects_above_100() {
    assert_eq!(Percentage::new(101), Err(OutOfRange(101)));
}

#[test]
fn rejects_large_without_truncation() {
    assert_eq!(Percentage::new(255), Err(OutOfRange(255)));
}
