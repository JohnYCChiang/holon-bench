use martial_los::{has_los, Grid};

#[test]
fn clear_diagonal_is_visible() {
    let g = Grid { width: 5, height: 5, blocked: vec![] };
    assert!(has_los(&g, (0, 0), (4, 4)));
}

#[test]
fn wall_between_blocks_sight() {
    let g = Grid { width: 5, height: 5, blocked: vec![(2, 2)] };
    assert!(!has_los(&g, (0, 0), (4, 4)));
}

#[test]
fn adjacent_cells_always_visible() {
    let g = Grid { width: 5, height: 5, blocked: vec![] };
    assert!(has_los(&g, (0, 0), (1, 0)));
}
