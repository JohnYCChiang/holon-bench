use std::marker::PhantomData;

pub struct Red;
pub struct Green;
pub struct Yellow;

/// A traffic light whose phase is tracked at the type level.
pub struct Light<S> {
    _state: PhantomData<S>,
}

impl Light<Red> {
    pub fn new() -> Light<Red> {
        Light { _state: PhantomData }
    }
    pub fn color(&self) -> &'static str {
        "red"
    }
    pub fn next(self) -> Light<Green> {
        Light { _state: PhantomData }
    }
}

impl Default for Light<Red> {
    fn default() -> Self {
        Self::new()
    }
}

impl Light<Green> {
    pub fn color(&self) -> &'static str {
        "green"
    }
    // BROKEN: green must advance to yellow, not skip back to red.
    pub fn next(self) -> Light<Red> {
        Light { _state: PhantomData }
    }
}

impl Light<Yellow> {
    pub fn color(&self) -> &'static str {
        "yellow"
    }
    pub fn next(self) -> Light<Red> {
        Light { _state: PhantomData }
    }
}
