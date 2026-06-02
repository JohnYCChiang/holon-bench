use crate::systems::combat::{apply_damage_events, collect_deaths, World};

pub fn run_combat_frame(world: &mut World) {
    collect_deaths(world);
    apply_damage_events(world);
}
