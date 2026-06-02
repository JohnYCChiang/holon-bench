use std::fs;

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct SaveGame {
    pub slot: String,
    pub payload: String,
}

pub fn save_game(save: &SaveGame) -> Result<(), String> {
    fs::write(format!("{}.save", save.slot), &save.payload).map_err(|err| err.to_string())
}

pub fn load_game(slot: &str) -> Result<SaveGame, String> {
    let payload = fs::read_to_string(format!("{slot}.save")).map_err(|err| err.to_string())?;
    Ok(SaveGame { slot: slot.to_string(), payload })
}
