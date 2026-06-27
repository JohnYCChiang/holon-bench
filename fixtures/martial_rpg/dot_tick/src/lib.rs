//! Authoritative damage-over-time (DoT) model. Damage is applied tick-accurately:
//! exactly one application every `period` game ticks, for a fixed number of
//! applications. Damage is applied per tick (never lump-summed) and clamps the
//! target's HP at 0.

pub struct Dot {
    remaining: u32,
    period: u32,
    tick_damage: u32,
    elapsed: u32,
}

impl Dot {
    /// `applications` damage events, one every `period` game ticks (a period of
    /// 0 is treated as 1), each dealing `tick_damage`.
    pub fn new(applications: u32, period: u32, tick_damage: u32) -> Self {
        Dot {
            remaining: applications,
            period,
            tick_damage,
            elapsed: 0,
        }
    }

    pub fn remaining(&self) -> u32 {
        self.remaining
    }

    /// Advance the DoT by one game tick against `hp`, returning the new hp.
    /// Damage is applied only on the tick that completes a full `period`.
    pub fn step(&mut self, hp: u32) -> u32 {
        // BUG: applies damage every tick, ignores the period and the remaining
        // count, and underflows hp instead of clamping at 0.
        self.remaining -= 1;
        hp - self.tick_damage
    }
}
