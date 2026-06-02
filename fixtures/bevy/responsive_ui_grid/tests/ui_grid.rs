use responsive_ui_grid::ui::{inventory_columns, GridConfig};

#[test]
fn narrow_layout_keeps_at_least_one_column() {
    let config = GridConfig { min_cell_width: 180, max_columns: 6 };

    assert_eq!(inventory_columns(120, config), 1);
}

#[test]
fn wide_layout_is_capped_by_max_columns() {
    let config = GridConfig { min_cell_width: 180, max_columns: 6 };

    assert_eq!(inventory_columns(1600, config), 6);
}
