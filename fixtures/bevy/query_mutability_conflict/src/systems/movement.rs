#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Actor {
    pub id: u32,
    pub x: i32,
    pub frozen: bool,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Target {
    pub actor_id: u32,
    pub x: i32,
    pub blocked: bool,
}

pub fn movement_system(actors: &mut [Actor], targets: &[Target]) {
    for actor in actors {
        if let Some(target) = targets.iter().find(|target| target.actor_id == actor.id) {
            actor.x = target.x;
        }
    }
}
