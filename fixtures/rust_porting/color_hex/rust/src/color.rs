pub fn hex_to_rgb(input: &str) -> String {
    let raw: String = input.trim().trim_start_matches('#').to_lowercase();
    let is_hex = |s: &str| !s.is_empty() && s.chars().all(|c| c.is_ascii_hexdigit());
    if raw.len() == 6 && is_hex(&raw) {
        let r = u32::from_str_radix(&raw[0..2], 16).unwrap();
        let g = u32::from_str_radix(&raw[2..4], 16).unwrap();
        let b = u32::from_str_radix(&raw[4..6], 16).unwrap();
        format!("{},{},{}", r, g, b)
    } else {
        "error".to_string()
    }
}
