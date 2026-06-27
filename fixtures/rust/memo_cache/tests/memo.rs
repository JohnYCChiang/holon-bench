use std::cell::Cell;
use std::rc::Rc;

use memo_cache::memo::Memo;

#[test]
fn computes_each_key_only_once() {
    let calls = Rc::new(Cell::new(0u32));
    let c = calls.clone();
    let memo = Memo::new(move |x| {
        c.set(c.get() + 1);
        x * x
    });

    assert_eq!(memo.get(4), 16);
    assert_eq!(memo.get(4), 16);
    assert_eq!(calls.get(), 1);

    assert_eq!(memo.get(5), 25);
    assert_eq!(calls.get(), 2);
}

#[test]
fn tracks_cached_entry_count() {
    let memo = Memo::new(|x| x + 1);
    assert!(memo.is_empty());
    memo.get(1);
    memo.get(2);
    memo.get(1);
    assert_eq!(memo.len(), 2);
}
