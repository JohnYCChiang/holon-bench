#[derive(Debug, PartialEq, Eq)]
pub struct Event {
    pub player: String,
    pub points: i32,
}

pub fn summarize(events: Vec<Event>) -> (usize, i32) {
    let total = events.iter().map(|event| event.points).sum();
    (events.len(), total)
}
