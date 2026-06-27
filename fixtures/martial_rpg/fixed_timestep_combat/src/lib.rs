//! Fixed-timestep combat model. `tick` advances exactly one authoritative
//! timestep and must be deterministic and bounds-safe.

pub struct Combatant {
    pub stamina: u32,
    pub max_stamina: u32,
    pub cooldown: u32,
}

impl Combatant {
    pub fn new(max_stamina: u32) -> Self {
        Combatant {
            stamina: max_stamina,
            max_stamina,
            cooldown: 0,
        }
    }

    /// Advance one fixed timestep: cooldown counts down toward 0 and holds there;
    /// stamina regenerates by 5 but never exceeds `max_stamina`.
    pub fn tick(&mut self) {
        self.cooldown -= 1; // BUG: underflows when cooldown is already 0
        self.stamina += 5; // BUG: can exceed max_stamina
    }

    /// Use an ability costing `cost` stamina and setting cooldown to `cd`.
    /// Returns false with no effect if on cooldown or stamina is insufficient.
    pub fn use_ability(&mut self, cost: u32, cd: u32) -> bool {
        if self.cooldown == 0 && self.stamina >= cost {
            self.stamina -= cost;
            self.cooldown = cd;
            true
        } else {
            false
        }
    }
}
