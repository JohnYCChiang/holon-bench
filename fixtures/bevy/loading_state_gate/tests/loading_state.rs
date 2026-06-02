use loading_state_gate::loading::{next_state, AssetStatus, GameState};

#[test]
fn loading_waits_until_all_required_assets_are_ready() {
    let partial = AssetStatus { required: 3, ready: 2, failed: false };
    assert_eq!(next_state(GameState::Loading, &partial), GameState::Loading);

    let complete = AssetStatus { required: 3, ready: 3, failed: false };
    assert_eq!(next_state(GameState::Loading, &complete), GameState::Playing);
}

#[test]
fn failed_assets_enter_failed_state() {
    let failed = AssetStatus { required: 3, ready: 1, failed: true };
    assert_eq!(next_state(GameState::Loading, &failed), GameState::Failed);
}
