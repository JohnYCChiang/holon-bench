use builder_validation::builder::{BuildError, Config, ConfigBuilder};

#[test]
fn validates_builder_before_building() {
    assert_eq!(ConfigBuilder::default().timeout_ms(5).build(), Err(BuildError::MissingEndpoint));
    assert_eq!(
        ConfigBuilder::default().endpoint("http://localhost").timeout_ms(0).build(),
        Err(BuildError::InvalidTimeout)
    );
    assert_eq!(
        ConfigBuilder::default().endpoint("http://localhost").timeout_ms(5).build(),
        Ok(Config { endpoint: "http://localhost".to_string(), timeout_ms: 5 })
    );
}
