use serde_json::Value;
use sha2::{Digest, Sha256};

pub fn cache_key(payload: &Value) -> String {
    let canonical = serde_json::to_string(payload).unwrap();
    let digest = Sha256::digest(canonical.as_bytes());
    format!("{digest:x}")
}
