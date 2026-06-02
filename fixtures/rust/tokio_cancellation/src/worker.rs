use std::sync::Arc;
use tokio::sync::{watch, Mutex};
use tokio::task::JoinHandle;

pub struct Worker {
    stop: watch::Sender<bool>,
    task: JoinHandle<()>,
}

impl Worker {
    pub fn spawn(resource: Arc<Mutex<u32>>) -> Self {
        let (stop, _receiver) = watch::channel(false);
        let task = tokio::spawn(async move {
            let mut locked = resource.lock().await;
            *locked += 1;
            loop {
                tokio::task::yield_now().await;
            }
        });
        Self { stop, task }
    }

    pub async fn cancel(self) {
        let _ = self.stop.send(true);
        let _ = self.task.await;
    }
}
