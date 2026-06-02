use result_aggregation::aggregate::{aggregate, Summary};

#[test]
fn preserves_successes_and_collects_all_errors() {
    let summary = aggregate(vec![
        Ok(1),
        Err("shard-a".to_string()),
        Ok(3),
        Err("shard-b".to_string()),
    ]);
    assert_eq!(
        summary,
        Summary {
            ok: false,
            values: vec![1, 3],
            errors: vec!["shard-a".to_string(), "shard-b".to_string()],
        }
    );
}
