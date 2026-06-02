use serde::Serialize;
use std::collections::HashMap;
use std::process::Command;
use std::time::Duration;

#[derive(Debug, Serialize)]
pub struct ProcessResult {
    pub stdout: String,
    pub stderr: String,
    pub exit_code: i32,
    pub timed_out: bool,
    pub duration_ms: u128,
}

pub fn run_command(
    program: &str,
    args: &[&str],
    environment: &HashMap<String, String>,
    _allowed_environment: &[&str],
    _timeout: Duration,
) -> ProcessResult {
    let output = Command::new(program)
        .args(args)
        .envs(environment)
        .output()
        .unwrap();
    ProcessResult {
        stdout: String::from_utf8_lossy(&output.stdout).to_string(),
        stderr: String::from_utf8_lossy(&output.stderr).to_string(),
        exit_code: output.status.code().unwrap_or(-1),
        timed_out: false,
        duration_ms: 0,
    }
}
