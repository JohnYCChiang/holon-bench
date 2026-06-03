use input_action_mapping::input::{actions_for_input, Action, InputState};

#[test]
fn hidden_deadzone_boundary_does_not_trigger_movement() {
    let actions = actions_for_input(
        InputState {
            axis_x: 0.15,
            jump_pressed: false,
        },
        0.15,
    );

    assert!(actions.is_empty(), "deadzone boundary should be suppressed");
}

#[test]
fn hidden_negative_axis_inside_deadzone_preserves_jump_only() {
    let actions = actions_for_input(
        InputState {
            axis_x: -0.14,
            jump_pressed: true,
        },
        0.15,
    );

    assert_eq!(actions, vec![Action::Jump]);
}
