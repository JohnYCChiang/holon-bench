#[derive(Debug)]
pub struct Record {
    pub id: String,
    pub active: bool,
}

#[derive(Debug, PartialEq, Eq)]
pub struct RecordView {
    pub id: String,
}

pub fn active_views(records: &[Record]) -> Vec<RecordView> {
    records
        .iter()
        .filter(|record| record.active)
        .map(|record| RecordView { id: record.id.clone() })
        .collect()
}
