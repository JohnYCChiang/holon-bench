use custom_ordering::tasks::{sort_tasks, Task};

#[test]
fn higher_priority_comes_first() {
    let mut v = vec![Task::new(1, "low"), Task::new(5, "high"), Task::new(3, "mid")];
    sort_tasks(&mut v);
    let order: Vec<&str> = v.iter().map(|t| t.name.as_str()).collect();
    assert_eq!(order, vec!["high", "mid", "low"]);
}

#[test]
fn ties_break_by_name_ascending() {
    let mut v = vec![Task::new(2, "beta"), Task::new(2, "alpha")];
    sort_tasks(&mut v);
    let order: Vec<&str> = v.iter().map(|t| t.name.as_str()).collect();
    assert_eq!(order, vec!["alpha", "beta"]);
}
