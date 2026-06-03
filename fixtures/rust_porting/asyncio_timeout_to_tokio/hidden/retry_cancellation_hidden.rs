use asyncio_timeout_to_tokio::{retry_with_timeout, RetryResult};
use std::cell::Cell;
use std::rc::Rc;
use std::time::{Duration, Instant};

struct DropCounter {
    drops: Rc<Cell<usize>>,
}

impl Drop for DropCounter {
    fn drop(&mut self) {
        self.drops.set(self.drops.get() + 1);
    }
}

#[tokio::test(flavor = "current_thread")]
async fn hidden_timeout_cancels_in_flight_operation_each_attempt() {
    let calls = Rc::new(Cell::new(0));
    let drops = Rc::new(Cell::new(0));
    let call_counter = Rc::clone(&calls);
    let drop_counter = Rc::clone(&drops);

    let started = Instant::now();
    let result = retry_with_timeout(3, Duration::from_millis(10), move || {
        call_counter.set(call_counter.get() + 1);
        let guard = DropCounter {
            drops: Rc::clone(&drop_counter),
        };
        async move {
            let _guard = guard;
            tokio::time::sleep(Duration::from_millis(250)).await;
            "late".to_string()
        }
    })
    .await;

    match result {
        RetryResult::Error { ok, error } => {
            assert!(!ok);
            assert_eq!(error.code, "timeout");
            assert_eq!(error.attempts, 3);
        }
        RetryResult::Success { .. } => panic!("slow operation should time out"),
    }
    assert_eq!(calls.get(), 3);
    assert_eq!(drops.get(), 3, "timed-out futures must be dropped");
    assert!(
        started.elapsed() < Duration::from_millis(150),
        "retry loop waited for the slow operation instead of cancelling it"
    );
}
