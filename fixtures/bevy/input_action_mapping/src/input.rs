#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Action {
    MoveLeft,
    MoveRight,
    Jump,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct InputState {
    pub axis_x: f32,
    pub jump_pressed: bool,
}

pub fn actions_for_input(input: InputState, _deadzone: f32) -> Vec<Action> {
    let mut actions = Vec::new();
    if input.axis_x < 0.0 {
        actions.push(Action::MoveLeft);
    } else if input.axis_x > 0.0 {
        actions.push(Action::MoveRight);
    }
    if input.jump_pressed {
        actions.push(Action::Jump);
    }
    actions
}
