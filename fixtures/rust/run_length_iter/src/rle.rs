pub struct RunLength {
    runs: std::vec::IntoIter<(char, usize)>,
    current: Option<(char, usize)>,
}

impl RunLength {
    pub fn new(runs: Vec<(char, usize)>) -> RunLength {
        RunLength { runs: runs.into_iter(), current: None }
    }
}

impl Iterator for RunLength {
    type Item = char;

    fn next(&mut self) -> Option<char> {
        // BROKEN: never expands runs.
        None
    }
}
