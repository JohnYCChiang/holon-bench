use asyncio_timeout_to_tokio::{retry_with_timeout, RetryResult};
use serde_json::Value;
use std::cell::Cell;
use std::process::Command;
use std::rc::Rc;
use std::time::Duration;

#[tokio::test(flavor = "current_thread")]
async fn timeout_retries_exactly_like_python_reference() {
    let calls = Rc::new(Cell::new(0));
    let call_counter = calls.clone();
    let result = retry_with_timeout(3, Duration::from_millis(10), move || {
        call_counter.set(call_counter.get() + 1);
        async {
            tokio::time::sleep(Duration::from_millis(100)).await;
            "late".to_string()
        }
    })
    .await;

    let script = concat!(env!("CARGO_MANIFEST_DIR"), "/../python/reference.py");
    let output = Command::new("python3").args([script, "3"]).output().unwrap();
    let python: Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(serde_json::to_value(result).unwrap(), python);
    assert_eq!(calls.get(), 3);
}

#[tokio::test(flavor = "current_thread")]
async fn success_stops_retrying() {
    let calls = Rc::new(Cell::new(0));
    let call_counter = calls.clone();
    let result = retry_with_timeout(3, Duration::from_millis(100), move || {
        call_counter.set(call_counter.get() + 1);
        async { "ready".to_string() }
    })
    .await;
    assert_eq!(
        result,
        RetryResult::Success {
            ok: true,
            value: "ready".to_string()
        }
    );
    assert_eq!(calls.get(), 1);
}
