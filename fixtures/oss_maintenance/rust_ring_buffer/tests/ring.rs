use ring_buffer::RingBuffer;

#[test]
fn overwrites_oldest_after_wrap() {
    let mut rb: RingBuffer<i32> = RingBuffer::new(3);
    for x in [1, 2, 3, 4, 5] {
        rb.push(x);
    }
    assert_eq!(rb.to_vec(), vec![3, 4, 5]);
}
