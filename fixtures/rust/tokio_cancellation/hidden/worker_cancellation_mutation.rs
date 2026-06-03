use std::sync::Arc;
use tokio::sync::Mutex;
use tokio::time::{timeout, Duration};
use tokio_cancellation::Worker;

#[tokio::test(flavor = "current_thread")]
async fn mutation_cancel_drops_background_task_resource_reference() {
    let resource = Arc::new(Mutex::new(0));
    let worker = Worker::spawn(resource.clone());
    tokio::task::yield_now().await;

    timeout(Duration::from_millis(100), worker.cancel())
        .await
        .expect("cancel must stop and join background task");

    assert_eq!(
        Arc::strong_count(&resource),
        1,
        "background task must not keep owning the resource after cancel"
    );
}
