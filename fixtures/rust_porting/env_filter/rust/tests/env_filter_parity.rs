use env_filter::env_filter::filter_env;
use std::collections::BTreeMap;
use std::process::Command;

fn python(payload: &str) -> String {
    let script = concat!(env!("CARGO_MANIFEST_DIR"), "/../python/reference.py");
    let output = Command::new("python3").args([script, payload]).output().unwrap();
    assert!(output.status.success());
    String::from_utf8(output.stdout).unwrap().trim().to_string()
}

#[test]
fn filters_like_python_reference() {
    let mut env = BTreeMap::new();
    env.insert("SAFE".to_string(), "1".to_string());
    env.insert("SECRET".to_string(), "x".to_string());
    env.insert("PATH".to_string(), "/evil".to_string());
    let allow = vec!["SAFE".to_string(), "PATH".to_string()];
    let keys = filter_env(&env, &allow).keys().cloned().collect::<Vec<_>>().join(",");
    let payload = r#"{"env":{"SAFE":"1","SECRET":"x","PATH":"/evil"},"allow":["SAFE","PATH"]}"#;
    assert_eq!(keys, python(payload));
}
