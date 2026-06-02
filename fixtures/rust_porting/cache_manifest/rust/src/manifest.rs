#[derive(Clone)]
pub struct Entry {
    pub path: String,
    pub bytes: usize,
    pub stale: bool,
}

pub fn summarize(entries: &[Entry]) -> String {
    let paths = entries.iter().map(|entry| entry.path.clone()).collect::<Vec<_>>().join(",");
    format!("paths={paths};bytes=0;stale=0")
}
