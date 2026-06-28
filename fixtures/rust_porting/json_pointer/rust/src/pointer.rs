use serde_json::Value;

fn not_found() -> Value {
    serde_json::json!({"error": "not_found"})
}

fn resolve(doc: &Value, pointer: &str) -> Value {
    if pointer.is_empty() {
        return doc.clone();
    }
    if !pointer.starts_with('/') {
        return not_found();
    }
    let mut cur = doc;
    for raw in pointer.split('/').skip(1) {
        let tok = raw.to_string();
        match cur {
            Value::Object(m) => match m.get(&tok) {
                Some(v) => cur = v,
                None => return not_found(),
            },
            Value::Array(a) => {
                if !tok.is_empty() && tok.chars().all(|c| c.is_ascii_digit()) {
                    let idx: usize = tok.parse().unwrap();
                    if idx < a.len() {
                        cur = &a[idx];
                    } else {
                        return not_found();
                    }
                } else {
                    return not_found();
                }
            }
            _ => return not_found(),
        }
    }
    cur.clone()
}

pub fn resolve_pointer(input: &str) -> String {
    let mut lines = input.split('\n');
    let doc: Value = serde_json::from_str(lines.next().unwrap_or("null")).unwrap();
    let pointer = lines.next().unwrap_or("");
    serde_json::to_string(&resolve(&doc, pointer)).unwrap()
}
