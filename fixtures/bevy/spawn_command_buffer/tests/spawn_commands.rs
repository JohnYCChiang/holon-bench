use spawn_command_buffer::spawn::{CommandBuffer, SpawnRequest, World};

#[test]
fn queued_spawns_apply_in_insertion_order_and_then_clear() {
    let mut world = World::default();
    let mut commands = CommandBuffer::default();
    commands.queue_spawn(SpawnRequest { name: "player".to_string() });
    commands.queue_spawn(SpawnRequest { name: "camera".to_string() });

    commands.apply(&mut world);

    assert_eq!(world.entities, vec!["player", "camera"]);
    assert!(commands.pending.is_empty());
}
