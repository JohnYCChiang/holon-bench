use crate::score::ScoreInput;

#[derive(Default, Debug)]
pub struct ScoreEvents {
    pub emitted: Vec<i32>,
}

pub fn emit_score(events: &mut ScoreEvents, input: ScoreInput) {
    let mut score = input.base + input.combo * 10;
    if input.perfect_clear {
        score += 100;
    }
    events.emitted.push(score);
}
