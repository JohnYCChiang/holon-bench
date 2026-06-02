pub struct PrefixAdapter<S> {
    inner: S,
    prefix: String,
}

impl<S> PrefixAdapter<S> {
    pub fn new(inner: S, prefix: impl Into<String>) -> Self {
        Self {
            inner,
            prefix: prefix.into(),
        }
    }
}
