#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Kind {
    Poison,
    Heal,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Status {
    pub id: u32,
    pub kind: Kind,
    pub amount: i32,
}

impl Status {
    pub fn new(id: u32, kind: Kind, amount: i32) -> Self {
        Status { id, kind, amount }
    }
}

fn rank(kind: Kind) -> u8 {
    match kind {
        Kind::Poison => 0,
        Kind::Heal => 1,
    }
}

/// Apply all statuses to `hp` for one tick. Poison removes `amount` percent of
/// the current hp (floored); Heal adds a flat `amount`. Statuses must resolve in
/// a deterministic order -- all poisons before all heals, each group ascending
/// by id -- so the result is independent of the input ordering. Hp is clamped at
/// zero after every step.
pub fn tick(hp: i32, statuses: &[Status]) -> i32 {
    // BUG: applies statuses in input order, so the result depends on ordering.
    let _ = rank(Kind::Poison);
    let mut h = hp;
    for s in statuses {
        match s.kind {
            Kind::Poison => h -= h * s.amount / 100,
            Kind::Heal => h += s.amount,
        }
        h = h.max(0);
    }
    h
}
