use scoring_logic_pure_module::score::{calculate_score, ScoreInput};
use scoring_logic_pure_module::systems::score::{emit_score, ScoreEvents};

#[test]
fn score_logic_is_pure_and_reused_by_system() {
    let input = ScoreInput {
        base: 50,
        combo: 3,
        perfect_clear: true,
    };

    assert_eq!(calculate_score(&input), 180);

    let mut events = ScoreEvents::default();
    emit_score(&mut events, input);
    assert_eq!(events.emitted, vec![180]);
}
