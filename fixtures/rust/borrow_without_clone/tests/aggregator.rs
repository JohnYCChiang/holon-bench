use borrow_without_clone::{Aggregator, LargePayload};

#[test]
fn aggregator_refreshes_total_without_changing_api() {
    let mut aggregator = Aggregator::new();
    aggregator.insert(
        "alpha".to_string(),
        LargePayload {
            samples: vec![2, 4, 8, 16],
        },
    );

    assert_eq!(aggregator.refresh_total("alpha"), Some(30));
    assert_eq!(aggregator.total("alpha"), Some(30));
    assert_eq!(aggregator.refresh_total("unknown"), None);
}
