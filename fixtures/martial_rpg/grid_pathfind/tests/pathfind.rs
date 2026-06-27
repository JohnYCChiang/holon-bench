use martial_pathfind::{shortest_cost, Grid, BLOCKED};

#[test]
fn terrain_cost_is_summed() {
    // 3x1 row, entering cell (1,0) costs 5 and (2,0) costs 1 -> total 6.
    let g = Grid { w: 3, h: 1, cost: vec![1, 5, 1] };
    assert_eq!(shortest_cost(&g, (0, 0), (2, 0)), Some(6));
}

#[test]
fn walls_force_a_detour() {
    // Cells (1,0) and (1,1) are blocked; path must go around the bottom.
    let g = Grid {
        w: 3,
        h: 3,
        cost: vec![1, BLOCKED, 1, 1, BLOCKED, 1, 1, 1, 1],
    };
    assert_eq!(shortest_cost(&g, (0, 0), (2, 0)), Some(6));
}
