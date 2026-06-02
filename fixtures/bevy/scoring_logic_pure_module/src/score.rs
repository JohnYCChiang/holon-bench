#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ScoreInput {
    pub base: i32,
    pub combo: i32,
    pub perfect_clear: bool,
}
