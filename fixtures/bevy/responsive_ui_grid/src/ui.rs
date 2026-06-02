#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct GridConfig {
    pub min_cell_width: u32,
    pub max_columns: u32,
}

pub fn inventory_columns(width: u32, config: GridConfig) -> u32 {
    let columns = width / config.min_cell_width;
    columns.min(config.max_columns)
}
