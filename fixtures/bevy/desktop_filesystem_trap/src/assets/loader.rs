use std::fs;
use std::io;

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct AssetConfig {
    pub root: String,
}

pub fn load_sprite_bytes(config: &AssetConfig, name: &str) -> io::Result<Vec<u8>> {
    fs::read(format!("{}/{}", config.root, name))
}
