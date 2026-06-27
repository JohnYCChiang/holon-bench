//! Authoritative spell-channel model. A channel runs for a fixed number of
//! ticks and breaks when it takes a hit meeting the interrupt threshold. The
//! server decides interruption from its own state; the client's claim is never
//! trusted.

pub struct Channel {
    pub remaining: u32,
    pub interrupt_threshold: u32,
    pub interrupted: bool,
    pub client_interrupted: bool,
}

impl Channel {
    pub fn new(duration: u32, interrupt_threshold: u32) -> Self {
        Channel {
            remaining: duration,
            interrupt_threshold,
            interrupted: false,
            client_interrupted: false,
        }
    }

    /// The channel is still active while it has not been interrupted and has
    /// ticks remaining.
    pub fn is_active(&self) -> bool {
        !self.interrupted && self.remaining > 0
    }

    /// Apply an incoming hit of `dmg`. The channel breaks only when it is still
    /// active and the hit meets the interrupt threshold.
    pub fn hit(&mut self, dmg: u32) {
        let _ = dmg;
        self.interrupted = self.client_interrupted; // BUG: trusts client, ignores threshold
    }

    /// Advance one tick. Returns true on the tick that completes the channel.
    pub fn tick(&mut self) -> bool {
        self.remaining -= 1; // BUG: underflows at 0; ignores interruption
        self.remaining == 0
    }
}
