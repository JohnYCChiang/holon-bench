/// A generational handle to a pooled projectile slot. The `generation`
/// distinguishes a live projectile from a stale handle whose slot has been
/// recycled.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Projectile {
    pub index: u32,
    pub generation: u32,
}

#[derive(Debug)]
pub struct ProjectilePool {
    capacity: usize,
    generations: Vec<u32>,
    active: Vec<bool>,
    free: Vec<u32>,
}

impl ProjectilePool {
    pub fn with_capacity(capacity: usize) -> Self {
        ProjectilePool {
            capacity,
            generations: Vec::new(),
            active: Vec::new(),
            free: Vec::new(),
        }
    }

    /// Acquire a projectile, recycling a freed slot when available, else
    /// growing up to `capacity`. Returns `None` when the pool is exhausted.
    pub fn acquire(&mut self) -> Option<Projectile> {
        if let Some(index) = self.free.pop() {
            self.active[index as usize] = true;
            Some(Projectile { index, generation: self.generations[index as usize] })
        } else if self.generations.len() < self.capacity {
            let index = self.generations.len() as u32;
            self.generations.push(0);
            self.active.push(true);
            Some(Projectile { index, generation: 0 })
        } else {
            None
        }
    }

    /// Release a live projectile back to the pool. A stale handle is rejected.
    /// Recycling must invalidate every existing handle to the slot.
    pub fn release(&mut self, p: Projectile) -> bool {
        if !self.is_live(p) {
            return false;
        }
        self.active[p.index as usize] = false;
        self.free.push(p.index);
        true
    }

    pub fn is_live(&self, p: Projectile) -> bool {
        let i = p.index as usize;
        i < self.active.len() && self.active[i] && self.generations[i] == p.generation
    }

    pub fn live_count(&self) -> usize {
        self.active.iter().filter(|&&a| a).count()
    }
}
