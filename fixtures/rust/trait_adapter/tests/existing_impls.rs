use trait_adapter::{EventSink, MemorySink};

#[test]
fn existing_sink_implementation_still_compiles_and_dispatches() {
    let sink = MemorySink::default();
    sink.send("plain");
    assert_eq!(sink.events(), vec!["plain".to_string()]);
}
