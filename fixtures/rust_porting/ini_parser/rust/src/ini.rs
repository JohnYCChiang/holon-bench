use serde_json::{Map, Value};

pub fn parse_ini(input: &str) -> String {
    let mut data: Map<String, Value> = Map::new();
    data.insert(String::new(), Value::Object(Map::new()));
    let mut section = String::new();
    for line in input.split('\n') {
        let s = line.trim();
        if s.is_empty() || s.starts_with(';') || s.starts_with('#') {
            continue;
        }
        if s.starts_with('[') && s.ends_with(']') {
            section = s[1..s.len() - 1].trim().to_string();
            data.entry(section.clone())
                .or_insert_with(|| Value::Object(Map::new()));
        } else if let Some(eq) = s.find('=') {
            let k = s[..eq].to_string();
            let v = s[eq + 1..].to_string();
            if let Some(Value::Object(m)) = data.get_mut(&section) {
                m.insert(k, Value::String(v));
            }
        }
    }
    if let Some(Value::Object(m)) = data.get("") {
        if m.is_empty() {
            data.remove("");
        }
    }
    serde_json::to_string(&Value::Object(data)).unwrap()
}
