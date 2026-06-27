use std::ops::Deref;

/// A thin wrapper around a Vec that derefs to a slice so callers can use
/// slice methods directly.
pub struct Stack<T> {
    items: Vec<T>,
}

impl<T> Stack<T> {
    pub fn new() -> Self {
        Stack { items: Vec::new() }
    }
    pub fn push(&mut self, value: T) {
        self.items.push(value);
    }
}

impl<T> Default for Stack<T> {
    fn default() -> Self {
        Self::new()
    }
}

impl<T> Deref for Stack<T> {
    type Target = [T];
    fn deref(&self) -> &[T] {
        // BROKEN: drops the bottom element and panics on an empty stack.
        &self.items[1..]
    }
}
