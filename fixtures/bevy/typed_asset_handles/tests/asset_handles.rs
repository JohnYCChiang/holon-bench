use typed_asset_handles::assets::{AssetRegistry, AudioHandle, SpriteHandle};

#[test]
fn sprite_and_audio_handles_do_not_cross_type_boundaries() {
    let mut registry = AssetRegistry::default();
    registry.insert_sprite("player", SpriteHandle(10));
    registry.insert_audio("theme", AudioHandle(20));

    assert_eq!(registry.sprite("player"), Some(SpriteHandle(10)));
    assert_eq!(registry.audio("theme"), Some(AudioHandle(20)));
    assert_eq!(registry.audio("player"), None);
    assert_eq!(registry.sprite("theme"), None);
}
