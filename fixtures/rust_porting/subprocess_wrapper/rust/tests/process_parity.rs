use serde_json::Value;
use std::collections::HashMap;
use std::process::Command;
use std::time::{Duration, Instant};
use subprocess_wrapper::run_command;

#[test]
fn environment_allowlist_matches_python_reference() {
    let mut env = HashMap::new();
    env.insert("PORT_ALLOWED".to_string(), "present".to_string());
    env.insert("PORT_SECRET".to_string(), "leak".to_string());
    let rust = run_command(
        "python3",
        &["-c", "import os; print(os.environ.get('PORT_ALLOWED', '')); print(os.environ.get('PORT_SECRET', 'missing'))"],
        &env,
        &["PORT_ALLOWED"],
        Duration::from_secs(2),
    );
    let script = concat!(env!("CARGO_MANIFEST_DIR"), "/../python/reference.py");
    let output = Command::new("python3").args([script, "present"]).output().unwrap();
    let python: Value = serde_json::from_slice(&output.stdout).unwrap();
    let mut rust = serde_json::to_value(rust).unwrap();
    assert!(rust["duration_ms"].as_u64().is_some());
    rust.as_object_mut().unwrap().remove("duration_ms");
    assert_eq!(rust, python);
}

#[test]
fn timeout_kills_direct_child_without_shell_expansion() {
    let started = Instant::now();
    let result = run_command(
        "python3",
        &["-c", "import time; time.sleep(2)"],
        &HashMap::new(),
        &[],
        Duration::from_millis(80),
    );
    assert!(result.timed_out);
    assert_ne!(result.exit_code, 0);
    assert!(result.duration_ms < 1000);
    assert!(started.elapsed() < Duration::from_secs(1));
}
