#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Event {
    Collision(u32, u32),
    AudioCue(&'static str),
    Score(u32),
}

pub fn drain_collisions(events: &mut Vec<Event>) -> Vec<(u32, u32)> {
    let mut collisions = Vec::new();
    for event in events.drain(..) {
        if let Event::Collision(a, b) = event {
            collisions.push((a, b));
        }
    }
    collisions
}
