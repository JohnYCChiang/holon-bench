use std::collections::BTreeMap;

pub fn filter_env(input: &BTreeMap<String, String>, allow: &[String]) -> BTreeMap<String, String> {
    let mut out = input.clone();
    for key in allow {
        out.entry(key.clone()).or_default();
    }
    out
}
