use state_machine::state::{transition, Event, State, TransitionError};

#[test]
fn accepts_valid_connection_lifecycle() {
    let state = transition(State::Disconnected, Event::Dial).unwrap();
    assert_eq!(state, State::Connecting);
    let state = transition(state, Event::Open).unwrap();
    assert_eq!(state, State::Connected);
    let state = transition(state, Event::Close).unwrap();
    assert_eq!(state, State::Closed);
}

#[test]
fn rejects_invalid_transitions() {
    assert_eq!(
        transition(State::Disconnected, Event::Open),
        Err(TransitionError::Invalid)
    );
    assert_eq!(
        transition(State::Closed, Event::Dial),
        Err(TransitionError::Invalid)
    );
}
