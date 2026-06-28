fn is_hex(c: char) -> bool {
    c.is_ascii_hexdigit()
}

fn dec(s: &str) -> String {
    let b: Vec<char> = s.chars().collect();
    let n = b.len();
    let mut out = String::new();
    let mut i = 0;
    while i < n {
        let c = b[i];
        if c == '%' && i + 2 < n && is_hex(b[i + 1]) && is_hex(b[i + 2]) {
            let hex: String = [b[i + 1], b[i + 2]].iter().collect();
            let v = u32::from_str_radix(&hex, 16).unwrap();
            out.push(char::from_u32(v).unwrap());
            i += 3;
        } else {
            out.push(c);
            i += 1;
        }
    }
    out
}

pub fn decode_query(input: &str) -> String {
    let data = input.trim_end_matches('\n');
    let mut out: Vec<String> = Vec::new();
    for part in data.split('&') {
        if part.is_empty() {
            continue;
        }
        let (key, val) = match part.find('=') {
            Some(p) => (&part[..p], &part[p + 1..]),
            None => (part, ""),
        };
        out.push(format!("{}={}", dec(key), dec(val)));
    }
    out.join(";")
}
