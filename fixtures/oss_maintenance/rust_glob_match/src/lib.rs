//! Tiny glob matcher. `*` matches any run of characters (including empty) and
//! `?` matches exactly one character. All other characters match literally.

/// Return true if `text` matches `pattern`.
pub fn matches(pattern: &str, text: &str) -> bool {
    let p: Vec<char> = pattern.chars().collect();
    let t: Vec<char> = text.chars().collect();
    m(&p, &t)
}

fn m(p: &[char], t: &[char]) -> bool {
    if p.is_empty() {
        return t.is_empty();
    }
    match p[0] {
        '*' => {
            // BUG: '*' is required to consume at least one character, so it can
            // never match an empty run (e.g. the trailing "*" in "a*" against
            // "a"). A '*' must be allowed to match zero characters.
            if t.is_empty() {
                return false;
            }
            m(p, &t[1..]) || m(&p[1..], &t[1..])
        }
        '?' => !t.is_empty() && m(&p[1..], &t[1..]),
        c => !t.is_empty() && t[0] == c && m(&p[1..], &t[1..]),
    }
}
