use std::collections::HashMap;
use std::time::Duration;
use subprocess_wrapper::run_command;

#[test]
fn hidden_empty_allowlist_does_not_inherit_parent_environment() {
    let mut env = HashMap::new();
    env.insert("PORT_SECRET".to_string(), "leak".to_string());

    let result = run_command(
        "python3",
        &[
            "-c",
            "import os; print(os.environ.get('HOME', 'missing')); print(os.environ.get('PORT_SECRET', 'missing'))",
        ],
        &env,
        &[],
        Duration::from_secs(2),
    );

    assert!(!result.timed_out);
    assert_eq!(result.exit_code, 0);
    assert_eq!(result.stderr, "");
    assert_eq!(result.stdout, "missing\nmissing\n");
}

#[test]
fn hidden_allowlist_passes_only_named_values() {
    let mut env = HashMap::new();
    env.insert("PORT_ALLOWED".to_string(), "present".to_string());
    env.insert("PORT_SECRET".to_string(), "leak".to_string());

    let result = run_command(
        "python3",
        &[
            "-c",
            "import os; print(os.environ.get('PORT_ALLOWED', 'missing')); print(os.environ.get('PORT_SECRET', 'missing'))",
        ],
        &env,
        &["PORT_ALLOWED"],
        Duration::from_secs(2),
    );

    assert!(!result.timed_out);
    assert_eq!(result.exit_code, 0);
    assert_eq!(result.stderr, "");
    assert_eq!(result.stdout, "present\nmissing\n");
}
