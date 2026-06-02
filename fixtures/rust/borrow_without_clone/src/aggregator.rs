use std::collections::HashMap;

pub struct LargePayload {
    pub samples: Vec<u64>,
}

pub struct Aggregator {
    payloads: HashMap<String, LargePayload>,
    totals: HashMap<String, u64>,
}

impl Aggregator {
    pub fn new() -> Self {
        Self {
            payloads: HashMap::new(),
            totals: HashMap::new(),
        }
    }

    pub fn insert(&mut self, key: String, payload: LargePayload) {
        self.payloads.insert(key, payload);
    }

    pub fn refresh_total(&mut self, key: &str) -> Option<u64> {
        let payload = self.payloads.get(key)?;
        self.set_total(key, payload.samples.iter().sum());
        Some(payload.samples.iter().sum())
    }

    fn set_total(&mut self, key: &str, total: u64) {
        self.totals.insert(key.to_string(), total);
    }

    pub fn total(&self, key: &str) -> Option<u64> {
        self.totals.get(key).copied()
    }
}
