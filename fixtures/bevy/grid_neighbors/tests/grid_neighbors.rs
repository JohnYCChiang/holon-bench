use grid_neighbors::neighbors::neighbors4;

#[test]
fn interior_cell_has_four_neighbors() {
    let n = neighbors4(5, 5, 2, 2);
    assert_eq!(n, vec![(2, 1), (2, 3), (1, 2), (3, 2)]);
}

#[test]
fn corner_cell_drops_out_of_bounds() {
    let n = neighbors4(5, 5, 0, 0);
    assert_eq!(n, vec![(0, 1), (1, 0)]);
}
