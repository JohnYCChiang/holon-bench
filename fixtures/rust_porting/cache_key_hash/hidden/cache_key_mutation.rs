use cache_key_hash::cache_key;
use serde_json::json;

#[test]
fn mutation_normalizes_strings_inside_nested_arrays_and_objects() {
    let payload = json!({
        "list": [
            {"z": " last ", "a": " first "},
            [" inner ", {"n": " val "}]
        ],
        "query": " q "
    });

    assert_eq!(
        cache_key(&payload),
        "bc9b4d42c54766691500689b7a7c8d0dbb24fdc60d6fc8b240981cae0b01f5fe"
    );
}
