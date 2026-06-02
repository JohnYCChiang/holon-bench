use std::sync::Arc;
use tokio::sync::Mutex;
use tokio::time::{timeout, Duration};
use tokio_cancellation::Worker;

#[tokio::test(flavor = "current_thread")]
async fn worker_cancellation_releases_resource_and_joins() {
    let resource = Arc::new(Mutex::new(0));
    let worker = Worker::spawn(resource.clone());
    tokio::task::yield_now().await;

    timeout(Duration::from_millis(100), worker.cancel())
        .await
        .expect("cancel must stop and join background task");

    let locked = resource.try_lock().expect("resource lock must be released");
    assert_eq!(*locked, 1);
}
