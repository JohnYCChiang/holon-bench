#[derive(Debug, PartialEq, Eq)]
pub struct Config {
    pub endpoint: String,
    pub timeout_ms: u64,
}

#[derive(Debug, PartialEq, Eq)]
pub enum BuildError {
    MissingEndpoint,
    InvalidTimeout,
}

#[derive(Default)]
pub struct ConfigBuilder {
    endpoint: Option<String>,
    timeout_ms: u64,
}

impl ConfigBuilder {
    pub fn endpoint(mut self, endpoint: impl Into<String>) -> Self {
        self.endpoint = Some(endpoint.into());
        self
    }

    pub fn timeout_ms(mut self, timeout_ms: u64) -> Self {
        self.timeout_ms = timeout_ms;
        self
    }

    pub fn build(self) -> Result<Config, BuildError> {
        Ok(Config {
            endpoint: self.endpoint.unwrap_or_default(),
            timeout_ms: self.timeout_ms,
        })
    }
}
