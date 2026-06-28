pub fn ordinals(input: &str) -> String {
    input
        .split_whitespace()
        .map(|t| {
            let n: i64 = t.parse().unwrap();
            let v = n.abs();
            let suf = match v % 10 {
                1 => "st",
                2 => "nd",
                3 => "rd",
                _ => "th",
            };
            format!("{}{}", n, suf)
        })
        .collect::<Vec<_>>()
        .join(" ")
}
