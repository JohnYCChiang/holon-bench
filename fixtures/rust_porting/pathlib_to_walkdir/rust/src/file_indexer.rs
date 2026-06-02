use serde::Serialize;
use std::path::Path;
use walkdir::WalkDir;

#[derive(Debug, PartialEq, Eq, Serialize)]
pub struct Skipped {
    pub hidden: usize,
    pub ignored: usize,
}

#[derive(Debug, PartialEq, Eq, Serialize)]
pub struct ScanResult {
    pub files: Vec<String>,
    pub skipped: Skipped,
}

pub fn scan_files(root: &Path, _excluded_suffix: &str) -> ScanResult {
    let files = WalkDir::new(root)
        .into_iter()
        .filter_map(Result::ok)
        .filter(|entry| entry.file_type().is_file())
        .map(|entry| {
            entry
                .path()
                .strip_prefix(root)
                .unwrap()
                .to_string_lossy()
                .to_string()
        })
        .collect();
    ScanResult {
        files,
        skipped: Skipped {
            hidden: 0,
            ignored: 0,
        },
    }
}
