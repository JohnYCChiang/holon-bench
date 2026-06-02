pub mod adapters;
pub mod traits;

pub use adapters::prefix::PrefixAdapter;
pub use traits::{EventSink, MemorySink};
