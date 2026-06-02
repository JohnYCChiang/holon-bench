use std::collections::BTreeMap;

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct SpriteHandle(pub u64);

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct AudioHandle(pub u64);

#[derive(Default, Debug)]
pub struct AssetRegistry {
    handles: BTreeMap<String, u64>,
}

impl AssetRegistry {
    pub fn insert_sprite(&mut self, key: impl Into<String>, handle: SpriteHandle) {
        self.handles.insert(key.into(), handle.0);
    }

    pub fn insert_audio(&mut self, key: impl Into<String>, handle: AudioHandle) {
        self.handles.insert(key.into(), handle.0);
    }

    pub fn sprite(&self, key: &str) -> Option<SpriteHandle> {
        self.handles.get(key).copied().map(SpriteHandle)
    }

    pub fn audio(&self, key: &str) -> Option<AudioHandle> {
        self.handles.get(key).copied().map(AudioHandle)
    }
}
