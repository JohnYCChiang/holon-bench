use std::sync::Arc;
use tokio::sync::Mutex;
use tokio::time::{timeout, Duration};
use tokio_cancellation::Worker;

#[tokio::test(flavor = "current_thread")]
async fn hidden_cancel_immediately_does_not_hang_or_hold_lock() {
    let resource = Arc::new(Mutex::new(0));
    let worker = Worker::spawn(resource.clone());

    timeout(Duration::from_millis(100), worker.cancel())
        .await
        .expect("immediate cancel must stop and join background task");

    let _locked = resource.try_lock().expect("resource lock must be released");
}

#[tokio::test(flavor = "current_thread")]
async fn hidden_cancel_many_workers_releases_every_resource() {
    let mut workers = Vec::new();
    let mut resources = Vec::new();

    for _ in 0..6 {
        let resource = Arc::new(Mutex::new(0));
        workers.push(Worker::spawn(resource.clone()));
        resources.push(resource);
    }

    tokio::task::yield_now().await;

    for worker in workers {
        timeout(Duration::from_millis(100), worker.cancel())
            .await
            .expect("each worker must stop without leaking a task");
    }

    for resource in resources {
        let _locked = resource.try_lock().expect("resource lock must be released");
    }
}
