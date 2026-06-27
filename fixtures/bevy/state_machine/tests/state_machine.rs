use state_machine::states::{next_state, Input, State};

#[test]
fn dead_is_terminal() {
    assert_eq!(next_state(State::Dead, Input::Move), State::Dead);
    assert_eq!(next_state(State::Dead, Input::JumpPress), State::Dead);
    assert_eq!(next_state(State::Dead, Input::Stop), State::Dead);
}

#[test]
fn basic_locomotion_transitions() {
    assert_eq!(next_state(State::Idle, Input::Move), State::Walk);
    assert_eq!(next_state(State::Walk, Input::Stop), State::Idle);
    assert_eq!(next_state(State::Idle, Input::JumpPress), State::Jump);
}
