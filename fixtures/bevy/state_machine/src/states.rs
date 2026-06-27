#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum State {
    Idle,
    Walk,
    Jump,
    Dead,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Input {
    Move,
    Stop,
    JumpPress,
    Land,
    Die,
}

/// Drive the character animation state machine.
///
/// Authoritative transition table:
/// - `Die` from any living state goes to `Dead`.
/// - `Dead` is terminal: no input escapes it.
/// - From `Idle`/`Walk`: `Move` -> Walk, `Stop` -> Idle, `JumpPress` -> Jump.
/// - From `Jump`: only `Land` returns to Idle; movement inputs are ignored
///   until the character lands.
/// - Any input not covered leaves the state unchanged.
pub fn next_state(current: State, input: Input) -> State {
    match (current, input) {
        (_, Input::Die) => State::Dead,
        (State::Idle, Input::Move) | (State::Walk, Input::Move) => State::Walk,
        (State::Idle, Input::Stop) | (State::Walk, Input::Stop) => State::Idle,
        (State::Idle, Input::JumpPress) | (State::Walk, Input::JumpPress) => State::Jump,
        (State::Jump, Input::Land) => State::Idle,
        (State::Dead, Input::Move) => State::Walk,
        _ => current,
    }
}
