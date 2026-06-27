use std::borrow::Cow;

/// Replace each tab with four spaces, allocating only when a tab is present.
pub fn normalize(input: &str) -> Cow<str> {
    // BROKEN: always allocates a new String even when there is nothing to change.
    Cow::Owned(input.replace('\t', "    "))
}
