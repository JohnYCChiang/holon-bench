//! Levenshtein edit distance between two strings, counted in Unicode scalar
//! values (`char`s), not bytes.

/// Return the minimum number of single-character insertions, deletions, or
/// substitutions that transform `a` into `b`.
pub fn distance(a: &str, b: &str) -> usize {
    // BUG: indexing the raw UTF-8 bytes counts a multibyte character as several
    // edits, so distance("café", "cafe") is 2 instead of 1. Edits are defined
    // over `char`s, so the strings must be compared character by character.
    let a = a.as_bytes();
    let b = b.as_bytes();
    let n = a.len();
    let m = b.len();
    let mut dp = vec![vec![0usize; m + 1]; n + 1];
    for i in 0..=n {
        dp[i][0] = i;
    }
    for j in 0..=m {
        dp[0][j] = j;
    }
    for i in 1..=n {
        for j in 1..=m {
            let cost = if a[i - 1] == b[j - 1] { 0 } else { 1 };
            dp[i][j] = (dp[i - 1][j] + 1)
                .min(dp[i][j - 1] + 1)
                .min(dp[i - 1][j - 1] + cost);
        }
    }
    dp[n][m]
}
