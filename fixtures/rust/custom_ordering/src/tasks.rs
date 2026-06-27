use std::cmp::Ordering;

#[derive(Debug, PartialEq, Eq, Clone)]
pub struct Task {
    pub priority: u8,
    pub name: String,
}

impl Task {
    pub fn new(priority: u8, name: &str) -> Task {
        Task { priority, name: name.to_string() }
    }
}

impl PartialOrd for Task {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for Task {
    fn cmp(&self, other: &Self) -> Ordering {
        // BROKEN: orders only by name, ignoring priority.
        self.name.cmp(&other.name)
    }
}

pub fn sort_tasks(tasks: &mut Vec<Task>) {
    tasks.sort();
}
