use trait_adapter::{EventSink, MemorySink, PrefixAdapter};

#[test]
fn adapter_dispatches_prefixed_events() {
    let sink = MemorySink::default();
    let adapter = PrefixAdapter::new(sink.clone(), "[audit] ");
    adapter.send("created");
    assert_eq!(sink.events(), vec!["[audit] created".to_string()]);
}
