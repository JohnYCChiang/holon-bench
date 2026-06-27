/// Build a stateful accumulator: each call adds its argument to a running total
/// and returns the new total.
pub fn make_accumulator(start: i64) -> impl FnMut(i64) -> i64 {
    let total = start;
    // BROKEN: the closure never updates `total`, so it does not accumulate.
    move |x| total + x
}
