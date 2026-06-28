use serde_json::Value;

pub fn merge_config(input: &str) -> String {
    let mut lines = input.split('\n');
    let base: Value = serde_json::from_str(lines.next().unwrap_or("null")).unwrap();
    let over: Value = serde_json::from_str(lines.next().unwrap_or("null")).unwrap();
    let merged = match (base, over) {
        (Value::Object(mut b), Value::Object(o)) => {
            for (k, v) in o {
                b.insert(k, v);
            }
            Value::Object(b)
        }
        (_, over) => over,
    };
    serde_json::to_string(&merged).unwrap()
}
