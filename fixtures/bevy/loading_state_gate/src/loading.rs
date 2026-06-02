#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum GameState {
    Loading,
    Playing,
    Failed,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct AssetStatus {
    pub required: usize,
    pub ready: usize,
    pub failed: bool,
}

pub fn next_state(current: GameState, assets: &AssetStatus) -> GameState {
    if assets.failed {
        return GameState::Failed;
    }
    if current == GameState::Loading && assets.ready > 0 {
        return GameState::Playing;
    }
    current
}
