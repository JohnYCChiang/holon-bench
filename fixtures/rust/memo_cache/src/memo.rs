use std::cell::RefCell;
use std::collections::HashMap;

pub struct Memo<F> {
    cache: RefCell<HashMap<u64, u64>>,
    compute: F,
}

impl<F: Fn(u64) -> u64> Memo<F> {
    pub fn new(compute: F) -> Memo<F> {
        Memo { cache: RefCell::new(HashMap::new()), compute }
    }

    pub fn get(&self, key: u64) -> u64 {
        // BROKEN: recomputes every time and never stores the result.
        (self.compute)(key)
    }

    pub fn len(&self) -> usize {
        self.cache.borrow().len()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }
}
