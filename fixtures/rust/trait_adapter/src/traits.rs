use std::sync::{Arc, Mutex};

pub trait EventSink {
    fn send(&self, event: &str);
}

#[derive(Clone, Default)]
pub struct MemorySink {
    events: Arc<Mutex<Vec<String>>>,
}

impl MemorySink {
    pub fn events(&self) -> Vec<String> {
        self.events.lock().unwrap().clone()
    }
}

impl EventSink for MemorySink {
    fn send(&self, event: &str) {
        self.events.lock().unwrap().push(event.to_string());
    }
}
