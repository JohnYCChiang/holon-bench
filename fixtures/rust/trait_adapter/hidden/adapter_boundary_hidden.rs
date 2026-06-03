use std::{cell::RefCell, rc::Rc};

use trait_adapter::{EventSink, PrefixAdapter};

struct RecordingSink {
    events: Rc<RefCell<Vec<String>>>,
}

impl RecordingSink {
    fn new(events: Rc<RefCell<Vec<String>>>) -> Self {
        Self { events }
    }
}

impl EventSink for RecordingSink {
    fn send(&self, event: &str) {
        self.events.borrow_mut().push(event.to_string());
    }
}

#[test]
fn prefix_adapter_works_with_external_event_sink_without_extra_trait_methods() {
    let events = Rc::new(RefCell::new(Vec::new()));
    let sink = RecordingSink::new(Rc::clone(&events));
    let adapter = PrefixAdapter::new(sink, "[combat] ");

    adapter.send("hit");
    adapter.send("block");

    assert_eq!(
        events.borrow().clone(),
        vec!["[combat] hit".to_string(), "[combat] block".to_string()]
    );
}
