pub trait Animal {
    fn name(&self) -> &str;
    fn legs(&self) -> u32;

    fn describe(&self) -> String {
        // BROKEN: default description ignores name and legs.
        String::new()
    }
}

pub struct Dog {
    pub name: String,
}

impl Animal for Dog {
    fn name(&self) -> &str {
        &self.name
    }
    fn legs(&self) -> u32 {
        4
    }
}

pub struct Snake {
    pub name: String,
}

impl Animal for Snake {
    fn name(&self) -> &str {
        &self.name
    }
    fn legs(&self) -> u32 {
        0
    }
}

pub struct Spider {
    pub name: String,
}

impl Animal for Spider {
    fn name(&self) -> &str {
        &self.name
    }
    fn legs(&self) -> u32 {
        8
    }
    fn describe(&self) -> String {
        format!("{} is a spooky spider with {} legs", self.name(), self.legs())
    }
}
