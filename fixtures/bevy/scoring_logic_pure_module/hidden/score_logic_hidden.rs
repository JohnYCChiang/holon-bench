use scoring_logic_pure_module::score::{calculate_score, ScoreInput};
use scoring_logic_pure_module::systems::score::{emit_score, ScoreEvents};

#[test]
fn hidden_system_reuses_pure_score_logic_for_multiple_events() {
    let inputs = vec![
        ScoreInput {
            base: 0,
            combo: 0,
            perfect_clear: false,
        },
        ScoreInput {
            base: 25,
            combo: 4,
            perfect_clear: false,
        },
        ScoreInput {
            base: 10,
            combo: 1,
            perfect_clear: true,
        },
    ];

    let expected: Vec<i32> = inputs.iter().map(calculate_score).collect();
    assert_eq!(expected, vec![0, 65, 120]);

    let mut events = ScoreEvents::default();
    for input in inputs {
        emit_score(&mut events, input);
    }

    assert_eq!(events.emitted, expected);
}
