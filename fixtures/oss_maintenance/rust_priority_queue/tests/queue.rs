use prio_queue::PriorityQueue;

#[test]
fn equal_priority_is_fifo() {
    let mut q = PriorityQueue::new();
    q.push(5, "a".into());
    q.push(5, "b".into());
    assert_eq!(q.pop(), Some("a".to_string()));
}
