use closure_accumulator::acc::make_accumulator;

#[test]
fn accumulates_from_zero() {
    let mut acc = make_accumulator(0);
    assert_eq!(acc(10), 10);
    assert_eq!(acc(5), 15);
    assert_eq!(acc(-3), 12);
}

#[test]
fn respects_start() {
    let mut acc = make_accumulator(100);
    assert_eq!(acc(1), 101);
}
