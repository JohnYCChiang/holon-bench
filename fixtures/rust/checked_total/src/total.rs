#[derive(Debug, PartialEq, Eq)]
pub enum BudgetError {
    Overflow,
}

/// Sum all values, returning an error instead of overflowing.
pub fn checked_total(values: &[i64]) -> Result<i64, BudgetError> {
    // BROKEN: plain summation overflows (panics in debug, wraps in release).
    let mut acc: i64 = 0;
    for &v in values {
        acc = acc + v;
    }
    Ok(acc)
}
