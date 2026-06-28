fn glob_match(p: &str, s: &str) -> bool {
    let p: Vec<char> = p.chars().collect();
    let s: Vec<char> = s.chars().collect();
    let (m, n) = (p.len(), s.len());
    let mut dp = vec![vec![false; n + 1]; m + 1];
    dp[0][0] = true;
    for i in 1..=m {
        for j in 1..=n {
            if p[i - 1] == '*' || p[i - 1] == '?' || p[i - 1] == s[j - 1] {
                dp[i][j] = dp[i - 1][j - 1];
            }
        }
    }
    dp[m][n]
}

pub fn match_glob(input: &str) -> String {
    let lines: Vec<&str> = input.split('\n').collect();
    let pattern = lines.first().copied().unwrap_or("");
    let candidates: Vec<&str> = lines[1..].iter().copied().filter(|l| !l.is_empty()).collect();
    let res: Vec<&str> = candidates
        .into_iter()
        .filter(|c| glob_match(pattern, c))
        .collect();
    res.join(",")
}
