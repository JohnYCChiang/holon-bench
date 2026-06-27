use time_convert::convert::{Hours, Minutes, Seconds};

#[test]
fn hours_to_seconds() {
    assert_eq!(Seconds::from(Hours(1)), Seconds(3600));
}

#[test]
fn minutes_to_seconds() {
    assert_eq!(Seconds::from(Minutes(3)), Seconds(180));
    assert_eq!(Minutes::from(Hours(2)), Minutes(120));
}
