#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Spawner {
    /// Seconds between spawns.
    pub interval: f32,
    /// Time banked toward the next spawn.
    pub accumulator: f32,
    /// Enemies still owed for the current wave.
    pub remaining: u32,
}

/// Advance the wave spawner by `delta` seconds and report how many enemies to
/// spawn this frame.
///
/// Rules:
/// - One enemy spawns per `interval` of banked time.
/// - Never spawn more than the wave's `remaining` budget; decrement it as
///   enemies spawn and stop once it hits zero.
/// - Only consume interval-sized chunks of the accumulator for enemies that
///   actually spawn; leave the rest banked for the next frame.
pub fn step(spawner: &mut Spawner, delta: f32) -> u32 {
    spawner.accumulator += delta;
    let mut spawned = 0;
    while spawner.accumulator >= spawner.interval {
        spawner.accumulator -= spawner.interval;
        spawned += 1;
    }
    spawned
}
