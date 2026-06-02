use desktop_filesystem_trap::assets::loader::{asset_request, AssetConfig};

#[test]
fn asset_paths_preserve_config_without_desktop_io() {
    let config = AssetConfig {
        root: "sprites".to_string(),
    };
    let request = asset_request(&config, "hero.png");

    assert_eq!(request.path, "sprites/hero.png");
    assert!(!request.uses_desktop_fs);
}
