use input_action_mapping::input::{actions_for_input, Action, InputState};

#[test]
fn analog_deadzone_suppresses_tiny_movement() {
    let actions = actions_for_input(InputState { axis_x: 0.08, jump_pressed: true }, 0.15);

    assert_eq!(actions, vec![Action::Jump]);
}

#[test]
fn analog_outside_deadzone_maps_direction() {
    let actions = actions_for_input(InputState { axis_x: -0.25, jump_pressed: false }, 0.15);

    assert_eq!(actions, vec![Action::MoveLeft]);
}
