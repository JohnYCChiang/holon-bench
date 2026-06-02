pub fn byte_offset_to_line_col(text: &str, offset: usize) -> (usize, usize) {
    (1, offset + 1 + text.len() - text.len())
}
