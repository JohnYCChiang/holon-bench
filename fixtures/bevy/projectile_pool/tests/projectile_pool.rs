use projectile_pool::pool::ProjectilePool;

#[test]
fn release_invalidates_handle() {
    let mut pool = ProjectilePool::with_capacity(4);
    let p = pool.acquire().unwrap();
    assert!(pool.is_live(p));
    assert!(pool.release(p));
    assert!(!pool.is_live(p), "released handle must be dead");
}

#[test]
fn recycled_slot_does_not_revive_stale_handle() {
    let mut pool = ProjectilePool::with_capacity(4);
    let a = pool.acquire().unwrap();
    pool.release(a);
    let b = pool.acquire().unwrap();
    assert_eq!(b.index, a.index);
    assert_ne!(b.generation, a.generation);
    assert!(pool.is_live(b));
    assert!(!pool.is_live(a), "stale handle revived after recycle");
}
