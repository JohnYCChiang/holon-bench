use inventory_stacking::inventory::{add_to_stacks, total};

#[test]
fn fills_partial_stack_then_spills_into_new_stack() {
    let mut stacks = vec![3];
    add_to_stacks(&mut stacks, 5, 4);
    // Top up the 3 to 5, then a new stack holds the remaining 2.
    assert_eq!(stacks, vec![5, 2]);
    assert_eq!(total(&stacks), 7);
}

#[test]
fn empty_inventory_gets_chunked_stacks() {
    let mut stacks: Vec<u32> = Vec::new();
    add_to_stacks(&mut stacks, 4, 10);
    assert_eq!(stacks, vec![4, 4, 2]);
}
