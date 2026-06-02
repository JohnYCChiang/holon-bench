use crate::components::Health;

pub fn is_alive(health: &Health) -> bool {
    health.current > 0
}
