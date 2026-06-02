use lifetime_view::view::{active_views, Record, RecordView};

#[test]
fn returns_borrowed_views_in_input_order() {
    let records = vec![
        Record { id: "a".to_string(), active: true },
        Record { id: "skip".to_string(), active: false },
        Record { id: "b".to_string(), active: true },
    ];
    let views: Vec<RecordView<'_>> = active_views(&records);
    assert_eq!(views, vec![RecordView { id: "a" }, RecordView { id: "b" }]);
}
