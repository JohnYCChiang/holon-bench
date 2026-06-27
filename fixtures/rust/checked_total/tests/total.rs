use checked_total::total::{checked_total, BudgetError};

#[test]
fn sums_normal_values() {
    assert_eq!(checked_total(&[1, 2, 3]), Ok(6));
}

#[test]
fn detects_overflow() {
    assert_eq!(checked_total(&[i64::MAX, 1]), Err(BudgetError::Overflow));
}
