#[derive(Clone, Debug, PartialEq, Eq)]
pub struct SpawnRequest {
    pub name: String,
}

#[derive(Default, Debug, PartialEq, Eq)]
pub struct World {
    pub entities: Vec<String>,
}

#[derive(Default, Debug, PartialEq, Eq)]
pub struct CommandBuffer {
    pub pending: Vec<SpawnRequest>,
}

impl CommandBuffer {
    pub fn queue_spawn(&mut self, request: SpawnRequest) {
        self.pending.push(request);
    }

    pub fn apply(&mut self, world: &mut World) {
        self.pending.clear();
        for request in &self.pending {
            world.entities.push(request.name.clone());
        }
    }
}
