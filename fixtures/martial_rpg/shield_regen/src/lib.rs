//! Authoritative energy shield with a post-damage regen delay. The server owns
//! the shield state: damage drains it and pauses regeneration for a fixed number
//! of ticks, after which it refills toward `max`.

pub struct Shield {
    pub current: u32,
    pub max: u32,
    pub regen_rate: u32,
    pub regen_delay: u32,
    pub delay_remaining: u32,
}

impl Shield {
    pub fn new(max: u32, regen_rate: u32, regen_delay: u32) -> Self {
        Shield {
            current: max,
            max,
            regen_rate,
            regen_delay,
            delay_remaining: 0,
        }
    }

    /// Apply incoming damage: drain the shield (never below 0) and restart the
    /// regen delay so regeneration pauses for `regen_delay` ticks.
    pub fn take_damage(&mut self, dmg: u32) {
        self.current -= dmg; // BUG: underflows when dmg > current
        self.delay_remaining = self.regen_delay;
    }

    /// Advance one fixed timestep. While `delay_remaining` is non-zero, count it
    /// down and do NOT regenerate; otherwise regenerate by `regen_rate`, capped
    /// at `max`.
    pub fn tick(&mut self) {
        self.current += self.regen_rate; // BUG: regenerates during the delay window and can exceed max
    }
}
