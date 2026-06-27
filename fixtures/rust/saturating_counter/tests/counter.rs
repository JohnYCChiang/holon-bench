use saturating_counter::counter::apply;

#[test]
fn saturates_high() {
    assert_eq!(apply(250, &[10]), 255);
}

#[test]
fn saturates_low() {
    assert_eq!(apply(5, &[-10]), 0);
}
