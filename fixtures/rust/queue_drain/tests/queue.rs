use queue_drain::queue::Queue;

#[test]
fn drains_fifo_up_to_limit_and_leaves_rest_queued() {
    let mut queue = Queue::default();
    queue.push(1);
    queue.push(2);
    queue.push(3);

    assert_eq!(queue.drain_ready(2), vec![1, 2]);
    assert_eq!(queue.drain_ready(2), vec![3]);
}
