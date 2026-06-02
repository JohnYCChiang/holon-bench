use error_source::error::ToolError;
use std::error::Error;
use std::io;

#[test]
fn wraps_io_error_and_preserves_source() {
    let source = io::Error::new(io::ErrorKind::NotFound, "missing config");
    let error = ToolError::from(source);
    assert_eq!(error.to_string(), "io failure");
    assert!(error.source().is_some());
    assert_eq!(error.source().unwrap().to_string(), "missing config");
}
