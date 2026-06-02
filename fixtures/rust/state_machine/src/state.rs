#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum State {
    Disconnected,
    Connecting,
    Connected,
    Closed,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Event {
    Dial,
    Open,
    Drop,
    Close,
}

#[derive(Debug, PartialEq, Eq)]
pub enum TransitionError {
    Invalid,
}

pub fn transition(state: State, event: Event) -> Result<State, TransitionError> {
    let _ = event;
    Ok(state)
}
