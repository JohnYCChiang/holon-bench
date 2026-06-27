use entity_allocator::allocator::Allocator;

#[test]
fn freeing_invalidates_the_handle() {
    let mut alloc = Allocator::new();
    let e1 = alloc.allocate();
    assert!(alloc.is_live(e1));
    alloc.free(e1);
    assert!(!alloc.is_live(e1), "freed handle must not be live");
}

#[test]
fn recycled_slot_does_not_revive_old_handle() {
    let mut alloc = Allocator::new();
    let e1 = alloc.allocate();
    alloc.free(e1);
    let e2 = alloc.allocate();
    // Same physical slot, but a fresh generation.
    assert_eq!(e2.index, e1.index);
    assert_ne!(e2.generation, e1.generation);
    assert!(alloc.is_live(e2));
    assert!(!alloc.is_live(e1), "stale handle must stay dead after recycle");
}
