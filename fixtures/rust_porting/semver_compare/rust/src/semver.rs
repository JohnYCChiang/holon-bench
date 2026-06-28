fn is_digits(s: &str) -> bool {
    !s.is_empty() && s.chars().all(|c| c.is_ascii_digit())
}

fn is_ident_char(c: char) -> bool {
    c.is_ascii_alphanumeric() || c == '-'
}

fn valid_num(s: &str) -> bool {
    is_digits(s) && (s.len() == 1 || !s.starts_with('0'))
}

fn parse(v: &str) -> Option<(u64, u64, u64, Vec<String>)> {
    let (core, build) = match v.split_once('+') {
        Some((c, b)) => (c, Some(b)),
        None => (v, None),
    };
    if let Some(b) = build {
        if b.is_empty()
            || !b
                .split('.')
                .all(|id| !id.is_empty() && id.chars().all(is_ident_char))
        {
            return None;
        }
    }
    let (main, pre) = match core.split_once('-') {
        Some((m, p)) => (m, Some(p)),
        None => (core, None),
    };
    let parts: Vec<&str> = main.split('.').collect();
    if parts.len() != 3 || !parts.iter().all(|p| valid_num(p)) {
        return None;
    }
    let major: u64 = parts[0].parse().ok()?;
    let minor: u64 = parts[1].parse().ok()?;
    let patch: u64 = parts[2].parse().ok()?;
    let pre_ids: Vec<String> = match pre {
        None => Vec::new(),
        Some(p) => {
            let ids: Vec<&str> = p.split('.').collect();
            for id in &ids {
                if id.is_empty() || !id.chars().all(is_ident_char) {
                    return None;
                }
                if is_digits(id) && id.len() > 1 && id.starts_with('0') {
                    return None;
                }
            }
            ids.into_iter().map(|s| s.to_string()).collect()
        }
    };
    Some((major, minor, patch, pre_ids))
}

pub fn compare(input: &str) -> String {
    let mut lines = input.split('\n');
    let a = lines.next().unwrap_or("");
    let b = lines.next().unwrap_or("");
    match (parse(a), parse(b)) {
        (Some(pa), Some(pb)) => {
            let ma = (pa.0, pa.1, pa.2);
            let mb = (pb.0, pb.1, pb.2);
            let r = if ma < mb {
                -1
            } else if ma > mb {
                1
            } else {
                0
            };
            format!("cmp={}", r)
        }
        _ => "error=invalid".to_string(),
    }
}
