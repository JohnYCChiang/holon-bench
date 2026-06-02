#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Health {
    pub current: i32,
    pub max: i32,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct HealthBundle {
    pub health: Health,
}

impl HealthBundle {
    pub fn new(max: i32) -> Self {
        Self {
            health: Health { current: max, max },
        }
    }
}
