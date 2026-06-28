pub fn check_luhn(input: &str) -> String {
    let raw = input.trim();
    let cleaned: String = raw.chars().filter(|c| *c != ' ' && *c != '-').collect();
    if cleaned.is_empty() || !cleaned.chars().all(|c| c.is_ascii_digit()) {
        return "valid=false;len=0".to_string();
    }
    let digits: Vec<u32> = cleaned.chars().map(|c| c.to_digit(10).unwrap()).collect();
    let mut total: u32 = 0;
    for (i, d) in digits.iter().rev().enumerate() {
        let mut d = *d;
        if i % 2 == 0 {
            d *= 2;
            if d > 9 {
                d -= 9;
            }
        }
        total += d;
    }
    let valid = total % 10 == 0;
    format!(
        "valid={};len={}",
        if valid { "true" } else { "false" },
        cleaned.len()
    )
}
