use crate::assets::loader::AssetConfig;

pub fn sprite_path(config: &AssetConfig, name: &str) -> String {
    format!("{}/{}", config.root, name)
}
