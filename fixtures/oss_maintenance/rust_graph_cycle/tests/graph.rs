use graph_topo::{topo_sort, GraphError};

#[test]
fn detects_simple_cycle() {
    // 0 -> 1 -> 2 -> 0
    assert_eq!(
        topo_sort(3, &[(0, 1), (1, 2), (2, 0)]),
        Err(GraphError::Cycle)
    );
}
