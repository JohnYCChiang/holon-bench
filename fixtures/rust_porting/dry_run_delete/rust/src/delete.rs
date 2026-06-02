use std::fs;
use std::path::PathBuf;

#[derive(Debug, PartialEq, Eq)]
pub struct DeleteReport {
    pub deleted: usize,
    pub would_delete: Vec<String>,
    pub skipped: Vec<String>,
}

pub fn delete_paths(paths: &[PathBuf], dry_run: bool) -> DeleteReport {
    let mut deleted = 0;
    let mut skipped = Vec::new();
    for path in paths {
        if path.exists() {
            let _ = fs::remove_file(path);
            deleted += 1;
        } else {
            skipped.push(path.file_name().unwrap().to_string_lossy().to_string());
        }
    }
    let _ = dry_run;
    DeleteReport { deleted, would_delete: Vec::new(), skipped }
}
