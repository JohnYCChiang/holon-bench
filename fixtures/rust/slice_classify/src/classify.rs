#[derive(Debug, PartialEq, Eq)]
pub enum Summary {
    Empty,
    Single(i32),
    Pair(i32, i32),
    Span { first: i32, last: i32, len: usize },
}

/// Classify a slice by its shape using slice patterns.
pub fn summarize(xs: &[i32]) -> Summary {
    match xs {
        [] => Summary::Empty,
        [x] => Summary::Single(*x),
        // BROKEN: collapses every slice of length >= 2 into a Pair of the first two.
        [a, b, ..] => Summary::Pair(*a, *b),
    }
}
