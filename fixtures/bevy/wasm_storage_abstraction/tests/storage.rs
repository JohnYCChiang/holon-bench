use std::collections::BTreeMap;

use wasm_storage_abstraction::storage::{load_game, save_game, SaveGame, Storage, StorageError};

#[derive(Default)]
struct MemoryStorage {
    values: BTreeMap<String, String>,
}

impl Storage for MemoryStorage {
    fn write(&mut self, key: &str, value: &str) -> Result<(), StorageError> {
        self.values.insert(key.to_string(), value.to_string());
        Ok(())
    }

    fn read(&self, key: &str) -> Result<String, StorageError> {
        self.values.get(key).cloned().ok_or_else(|| StorageError::NotFound(key.to_string()))
    }
}

#[test]
fn save_and_load_use_injected_storage() {
    let mut storage = MemoryStorage::default();
    let save = SaveGame { slot: "slot1".to_string(), payload: "level=2".to_string() };

    save_game(&mut storage, &save).unwrap();
    assert_eq!(load_game(&storage, "slot1").unwrap(), save);
}

#[test]
fn missing_save_uses_structured_error() {
    let storage = MemoryStorage::default();

    assert_eq!(load_game(&storage, "missing"), Err(StorageError::NotFound("missing".to_string())));
}
