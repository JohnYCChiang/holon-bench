#[derive(Clone, Debug, PartialEq, Eq)]
pub struct DamageEvent {
    pub entity: u32,
    pub amount: i32,
}

#[derive(Default, Debug)]
pub struct World {
    pub health: Vec<(u32, i32)>,
    pub pending_damage: Vec<DamageEvent>,
    pub deaths: Vec<u32>,
}

pub fn emit_damage(world: &mut World, entity: u32, amount: i32) {
    world.pending_damage.push(DamageEvent { entity, amount });
}

pub fn apply_damage_events(world: &mut World) {
    for event in world.pending_damage.drain(..) {
        if let Some((_, health)) = world.health.iter_mut().find(|(id, _)| *id == event.entity) {
            *health -= event.amount;
        }
    }
}

pub fn collect_deaths(world: &mut World) {
    for (entity, health) in &world.health {
        if *health <= 0 && !world.deaths.contains(entity) {
            world.deaths.push(*entity);
        }
    }
}
