#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub struct Hours(pub u64);
#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub struct Minutes(pub u64);
#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub struct Seconds(pub u64);

impl From<Hours> for Minutes {
    fn from(h: Hours) -> Self {
        Minutes(h.0 * 60)
    }
}

impl From<Minutes> for Seconds {
    fn from(m: Minutes) -> Self {
        Seconds(m.0 * 60)
    }
}

impl From<Hours> for Seconds {
    // BROKEN: should chain Hours -> Minutes -> Seconds; this only multiplies once.
    fn from(h: Hours) -> Self {
        Seconds(h.0 * 60)
    }
}
