use serde::Serialize;
use std::future::Future;
use std::time::Duration;

#[derive(Debug, PartialEq, Eq, Serialize)]
#[serde(untagged)]
pub enum RetryResult {
    Success { ok: bool, value: String },
    Error { ok: bool, error: RetryError },
}

#[derive(Debug, PartialEq, Eq, Serialize)]
pub struct RetryError {
    pub code: String,
    pub attempts: usize,
}

pub async fn retry_with_timeout<F, Fut>(
    _max_attempts: usize,
    _timeout: Duration,
    mut operation: F,
) -> RetryResult
where
    F: FnMut() -> Fut,
    Fut: Future<Output = String>,
{
    RetryResult::Success {
        ok: true,
        value: operation().await,
    }
}
